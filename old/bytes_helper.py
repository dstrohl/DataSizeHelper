from copy import copy
import math
from bytes_helper_lookups import *
import logging

log = logging.getLogger(__name__)

'''

Full Strict Set
"Mb, Mib, Mibibyte, Megabyte"



limit to dec/bin or limit to byte/bit

With Aliases
    Mg = Mb, meg = Mb
    long names
    capitalization
    if limiting, force convert to limited options.


    Alias Sets:
        'common_names', (CN)
        'long_names', (LN)
        'case_changes' (CC)
        'convert_filtered_units' (CFU)




fix_unit process:
    1. unit in limit_to set
        return unit

    2. if unitset not set, try to detect it using return to, limit_to, then default unitset.
        build best alias set:
        if unit in best alias set



'''
'''
ALIAS_GENERATORS = []

class BaseAliasGenerator(object):
    name = 'common_names'
    key = 'CN'

    def __init__(self, data_calc):
        self.dsc = data_calc

    def generate_aliases(self, unitset, alias_dict, unit_dict):
        raise NotImplementedError

    def __call__(self, unitset=None, alias_dict=None):
        return self.generate_aliases(unitset=unitset, alias_dict=alias_dict)



class CommonNameAliasGen(BaseAliasGenerator):
    name = 'common_names'
    key = 'CN'
    priority = 10

    def generate_aliases(self, unitset, alias_dict, unit_dict):

        tmp_ret = {}
        tmp_ret['meg'] = make_unit_name('M', unitset)
        tmp_ret['mg'] = make_unit_name('M', unitset)
        tmp_ret['Mg'] = make_unit_name('M', unitset)
        tmp_ret['gig'] = make_unit_name('G', unitset)
        tmp_ret['Meg'] = make_unit_name('M', unitset)
        tmp_ret['Gig'] = make_unit_name('G', unitset)

        return tmp_ret

ALIAS_GENERATORS.append(CommonNameAliasGen)



class AddExtraAliases(BaseAliasGenerator):
    name = 'extra-aliases'
    key = 'EA'
    priority = 10

    def generate_aliases(self, unitset, alias_dict, unit_dict):
        tmp_ret = {}
        if self.dsc._has_extra_aliases:
            for key, item in self.dsc._extra_aliases.items():
                if isinstance(item, str):
                    item = [item]
                for alias in item:
                    tmp_ret[alias] = key
        return tmp_ret


ALIAS_GENERATORS.append(AddExtraAliases)

class AddLongNameAliases(BaseAliasGenerator):
    name = 'long_names'
    key = 'LN'
    priority = 10

    def generate_aliases(self, unitset, alias_dict, unit_dict):
        tmp_ret = {}

        for unit in unit_dict:
            item = self.dsc._base_units[unit]
            tmp_ret[item['long']['name']] = item['short']['name']

        return tmp_ret

ALIAS_GENERATORS.append(AddLongNameAliases)

class WrongCaseAliasGen(BaseAliasGenerator):
    name = 'fix_case'
    key = 'FC'
    priority = 100

    def generate_aliases(self, unitset, alias_dict, unit_dict):

        tmp_ret = {}
        for key, item in BASEUNITS.items():
            short_name = make_unit_name(key, unitset)
            tmp_ret[key] = short_name                       # ex: "M"
            tmp_ret[key.lower()] = short_name               # ex: "m"

        for alias, key in unit_dict.items():
            alias_len = len(alias)
            if alias == 'B':
                if BIT not in unitset:
                    tmp_ret['b'] = key
            elif alias == 'b':
                if BYT not in unitset:
                    tmp_ret['B'] = key
            else:
                tmp_alias = alias[0].lower()+alias[1:]
                tmp_ret[tmp_alias] = key

        for alias, key in alias_dict.items():

            tmp_alias = alias[0].upper()+alias[1:]
            tmp_ret[tmp_alias] = key

            tmp_alias = alias.replace('byte', 'Byte')
            tmp_ret[tmp_alias] = key

            tmp_alias = alias.replace('bit', 'Bit')
            tmp_ret[tmp_alias] = key

        return tmp_ret

ALIAS_GENERATORS.append(WrongCaseAliasGen)
'''

class DataSizeOptions(object):
    _suffix_set_name = None
    _full_unit_list_name = None
    _suffix_sets = None
    _return_unit = None
    _limit_to = None
    _use_aliases = None
    _use_long_names = None
    _normalize = None

    def __init__(self, dso, **kwargs):
        self.dso = dso
        self._suffix_sets = None

        for key, value in kwargs.items():
            key = '_'+key
            setattr(self, key, value)

    @property
    def full_unit_list_name(self):
        tmp_ret = str(self.get_limit_to)
        if self.use_aliases:
            tmp_ret += ':UA=Y'
            if self.use_long_names:
                tmp_ret += ':ULN=Y'
            if self.dso.unitset is not None:
                tmp_ret += ':U='+self.dso.unitset
        return tmp_ret

    @property
    def return_unit(self):
        return self._return_unit

    def get_limit_to(self):
        return self._limit_to or self.dso._dsc._default_limit_to

    def set_limit_to(self, value):
        self._limit_to = value

    def get_use_aliases(self):
        return self._use_aliases or self.dso._dsc._default_use_aliases

    def set_use_aliases(self, value):
        self._use_aliases = value

    def get_use_long_names(self):
        return self._use_long_names or self.dso._dsc._default_use_long_names

    def set_use_long_names(self, value):
        self._limit_to = value

    @property
    def suffix_set_name(self):
        if self._suffix_set_name is None:
            self._suffix_set_name = str(self.suffix_sets)
        return self._suffix_set_name

    def get_suffix_sets(self):
        tmp_set = self._suffix_sets or self.dso._dsc._default_suffix_sets

        if isinstance(tmp_set, str):
            return [tmp_set]
        else:
            return tmp_set

    def set_suffix_sets(self, value):
        self._suffix_sets = value

    limit_to = property(fget=get_limit_to, fset=set_limit_to)
    use_aliases = property(fget=get_use_aliases, fset=set_use_aliases)
    use_long_names = property(fget=get_use_long_names, fset=set_use_long_names)
    suffix_sets = property(fget=get_suffix_sets, fset=set_suffix_sets)


class DataUnitManager(object):
    DECIMAL_BYTE = 'decimal-byte'
    DECIMAL_BIT = 'decimal-bit'
    BINARY_BYTE = 'binary-byte'
    BINARY_BIT = 'binary-bit'
    BIT = 'bit'
    BYTE = 'byte'
    BINARY = 'binary'
    DECIMAL = 'decimal'

    """
    Converts units of measure to valid ones.

    - will handle parsing of string values into value, unit, suffix.

    - has flags for allowing the following options:
        - long names
        - plural names
        - caps/lower and camel-case long names

    - if a unitset is defined,
        - can also handle non-specific alias's. (i.e. K = Kb etc...)
        - can force names into the defined unitset.

    """
    def __init__(self,
                 unitset=None,
                 allow_long_names=True,
                 allow_plural_names=True,
                 allow_incorrect_case=True,
                 force_non_specific=False,
                 force_to_unitset=False,

                 suffix_sets=None,

                 default_unit='B',

                 ):

        self.unitset = unitset
        self.allow_long_names = allow_long_names
        self.allow_plural_names = allow_plural_names
        self.allow_incorrect_case = allow_incorrect_case
        self.force_non_specific = force_non_specific
        self.force_to_unitset = False

        self.suffix_sets = suffix_sets
        self.default_unit = default_unit


    def update_aliases(self):


class DataSizeCalculator(object):

    """
    This object is intended to be instantiated once per app, then called by
    the helper...  this will force the harder calculations to happen just
    once and be cached during the duration of the app.
    """

    def __init__(self,

                 default_limit_to=None,
                 default_unitset=None,
                 default_unit='B',

                 default_suffix_sets='network',
                 extra_suffixes=None,

                 default_use_aliases=True,
                 default_use_long_names=True,
                 extra_aliases=None,
                 fallback_unitset=DEC_BYT,
                 cache_compiled_lookups=True,

                 ):
        """

        :param default_limit_to: any of the extended unitsets
        :param default_alias_sets: any valid alias_set_names or objects
        :param default_suffix_sets: currently only ['network'|None]
        :param extra_aliases: format of: {'<unit short name>': ['<alias_name>', '<alias_name>'...]}
        :param extra_suffixes: format of ['suffix valid use': ['suffix', 'suffix', ...]}

        :param cache_compiled_lookups:
        :return:
        """

        self._cache_compiled_lookups = cache_compiled_lookups

        self._default_use_aliases = default_use_aliases
        self._default_use_long_names = default_use_long_names
        self._extra_aliases = extra_aliases

        self._default_suffix_sets = default_suffix_sets

        self._default_unit = default_unit
        self._default_unitset = default_unitset
        self._default_limit_to = default_limit_to
        self._fallback_unitset = fallback_unitset

        self._has_extra_aliases = extra_aliases is not None

        self._base_units = {}
        self._unit_lists = {}
        self._suffixes = {}
        # self._alias_unit_lists = {}
        self._suffix_sets = SUFFIX_SETS.copy()

        if extra_suffixes is not None:
            self._suffix_sets.update(extra_suffixes)

        self._unitsets = {
            DEC_BIT: [('b', 1)],
            DEC_BYT: [('B', 1)],
            BIN_BIT: [('b', 1)],
            BIN_BYT: [('B', 1)]}

        self._make_initial()

    def _make_initial(self):
        for unit_key, unit_info in BASEUNITS.items():

            for us in UNITSET_NAMES:

                us_info = UNITSET_INFO[us]

                unit_short_name = make_unit_name(unit_key, us)
                unit_long_name = make_unit_name(unit_key, us, long=True)

                self._base_units[unit_short_name] = {}
                base_rec = self._base_units[unit_short_name]

                base_rec['base_key'] = unit_key
                base_rec['short'] = {}
                base_rec['long'] = {}
                base_rec['short']['name'] = unit_short_name
                base_rec['long']['name'] = unit_long_name

                if unit_key == 'B':
                    if BYT in us:
                        base_rec['unitset'] = BYT
                    else:
                        base_rec['unitset'] = BIT
                else:
                    base_rec['unitset'] = us

                base_rec[BIN] = us_info['bd'] == BIN or unit_key.lower() == 'b'
                base_rec[DEC] = us_info['bd'] == DEC or unit_key.lower() == 'b'
                base_rec[BIT] = us_info['bb'] == BIT or unit_key == 'b'
                base_rec[BYT] = us_info['bb'] == BYT or unit_key == 'B'

                base_rec['conversions'] = {}
                base_rec['conversions'][BIN] = make_unit_name(unit_key, merge_ext_unitsets(BIN, us, force_a=True))
                base_rec['conversions'][DEC] = make_unit_name(unit_key, merge_ext_unitsets(DEC, us, force_a=True))
                base_rec['conversions'][BIT] = make_unit_name(unit_key, merge_ext_unitsets(BIT, us, force_a=True))
                base_rec['conversions'][BYT] = make_unit_name(unit_key, merge_ext_unitsets(BYT, us, force_a=True))
                base_rec['conversions'][opposite_unitset(us)] = make_unit_name(unit_key, opposite_unitset(us))

                unit_to_b_mult = ((us_info['power'] ** unit_info['cm']) * us_info['mult'])

                self._unitsets[us].append((unit_short_name, unit_to_b_mult))

                base_rec['to'] = {}
                base_rec['to']['b'] = unit_to_b_mult

                '''
                self._unit_list['base'][unit_short_name] = unit_short_name

                if self._include_long_names:
                    self._unit_list['base'][unit_long_name] = unit_short_name
                    self._unit_list['base'][unit_long_name.capitalize()] = unit_short_name
                '''

        for item in self._unitsets.values():
            item.sort(key=lambda k: k[1])

    def _get_limit_to_list(self, limit_to, use_aliases=False, use_long_names=True, unitset=None):

        alias_set_name = str(limit_to)

        if use_aliases:
            alias_set_name += 'UA=Y'
            if use_long_names:
                alias_set_name += ':ULN=Y'
            if unitset is not None:
                alias_set_name += ':U='+unitset

        if self._cache_compiled_lookups:
            try:
                return self._unit_lists[alias_set_name]
            except KeyError:
                pass

        tmp_alias_set = {}

        for u in self._base_units.values():
            short_name = u['short']['name']
            if limit_to is None:
                tmp_alias_set[short_name] = short_name
            elif u['base_key'] == 'B' and u['unitset'] in limit_to:
                tmp_alias_set[short_name] = short_name
            elif limit_to in u['unitset']:
                tmp_alias_set[short_name] = short_name

        if use_aliases:
            if use_long_names:
                tmp_ln_set = {}
                for unit in tmp_alias_set:
                    item = self._base_units[unit]
                    tmp_long_name = item['long']['name']
                    short_name = item['short']['name']

                    tmp_alias = tmp_long_name
                    tmp_ln_set[tmp_alias] = short_name
                    tmp_ln_set[tmp_alias+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')+'s'] = short_name

                    tmp_alias = tmp_long_name.capitalize()
                    tmp_ln_set[tmp_alias] = short_name
                    tmp_ln_set[tmp_alias+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')+'s'] = short_name

                tmp_alias_set.update(tmp_ln_set)
            if self._has_extra_aliases:
                for key, item in self._extra_aliases.items():
                    if isinstance(item, str):
                        item = [item]
                    for alias in item:
                        tmp_alias_set[alias] = key

            if unitset is not None:

                tmp_alias_set['Mg'] = make_unit_name('M', unitset)
                tmp_alias_set['Meg'] = make_unit_name('M', unitset)
                tmp_alias_set['Gig'] = make_unit_name('G', unitset)

                for key, item in BASEUNITS.items():
                    short_name = make_unit_name(key, unitset)
                    tmp_alias_set[key] = short_name                       # ex: "M"
                    tmp_alias_set[key.lower()] = short_name               # ex: "m"

                tmp_case_set = {}
                for alias, key in tmp_alias_set.items():
                    alias_len = len(alias)
                    if alias == 'B':
                        if BIT not in unitset:
                            tmp_case_set['b'] = key
                    elif alias == 'b':
                        if BYT not in unitset:
                            tmp_case_set['B'] = key
                    elif 1 < alias_len < 4:
                        tmp_alias = alias[0].lower()+alias[1:]
                        tmp_case_set[tmp_alias] = key
                tmp_alias_set.update(tmp_case_set)

        if self._cache_compiled_lookups:
            self._unit_lists[alias_set_name] = tmp_alias_set

        return tmp_alias_set

    def _validate_unit(self, unit, limit_to):
        return unit in self._get_limit_to_list(limit_to=limit_to)

    def _fix_units(self, val_obj):

        if val_obj.valid_units():
            return

        unit_fixed = False
        return_fixed = val_obj.options.return_unit is None

        def try_fix(unit_fixed, return_fixed):
            tmp_unit_list = self._get_limit_to_list(
                limit_to=val_obj.options.limit_to,
                use_aliases=val_obj.options.use_aliases,
                use_long_names=val_obj.options.use_long_names,
                unitset=val_obj.unitset)

            if val_obj.unit in tmp_unit_list:
                val_obj.unit = tmp_unit_list[val_obj.unit]
                unit_fixed = True

            if val_obj.options.return_unit is not None:
                if val_obj.options._return_unit in tmp_unit_list:
                    val_obj.options._return_unit = tmp_unit_list[val_obj.options._return_unit]
                    return_fixed = True

            return unit_fixed, return_fixed



        unit_fixed, return_fixed = try_fix(unit_fixed, return_fixed)

        if unit_fixed and return_fixed:
            self._set_unitset(val_obj)
            return

        self._set_unitset(val_obj)

        unit_fixed, return_fixed = try_fix(unit_fixed, return_fixed)


        if not unit_fixed:
            raise AttributeError('Could not determine what units of measure %s is.' % val_obj.unit)
        if not return_fixed:
            raise AttributeError('Could not determine what units of measure %s is.' % val_obj.options.return_unit)

        return


    def _get_mult(self, from_unit, to_unit):
        tmp_from = self._base_units[from_unit]['to']
        try:
            return tmp_from[to_unit]
        except KeyError:
            tmp_from_bits = self._get_mult(from_unit, 'b')
            tmp_to_bits = self._get_mult(to_unit, 'b')
            tmp_from[to_unit] = tmp_from_bits / tmp_to_bits
            return tmp_from[to_unit]

    def _set_unitset(self, val_obj):

        if val_obj.unitset is not None:
            return

        def try_lookup(unit):
            unit_info = self._base_units[unit]
            if unit_info['base_key'] == 'B':
                return merge_ext_unitsets(unit_info['unitset'], self._default_unitset, force_a=True)
            else:
                return unit_info['unitset']

        if val_obj.unit is not None:
            try:
                val_obj.unitset = try_lookup(val_obj.unit)
                return
            except KeyError:
                if val_obj.options.return_unit is not None:
                    try:
                        val_obj.unitset = try_lookup(val_obj.options.return_unit)
                        return
                    except KeyError:
                        pass

        if val_obj.options.limit_to in UNITSET_NAMES:
            val_obj.unitset = val_obj.options.limit_to
            return

        if self._default_unitset is not None:
            val_obj.unitset = self._fallback_unitset
            return

        raise AttributeError('Unitset not detectable for %s' % val_obj)

    def convert(self, value, from_unit=None, to_unit='b'):
        tmp_value = value * self._get_mult(from_unit, to_unit)
        return tmp_value

    def normalize(self, val_obj):
        if val_obj.unitset is None:
            raise AttributeError('Unitset must be set in order to normalize information')

        base_value = self.convert(val_obj)
        norm_unit = 'b'
        for item in self._unitsets[val_obj.unitset]:
            if base_value.value < item[1]:
                break
            norm_unit = item[0]

        val_obj.value = self.convert(base_value, to_unit=norm_unit)
        val_obj.unit = norm_unit

    def _parse_item(self, val_obj):

        value = val_obj.value
        # suffix_sets = val_obj.options.suffix_sets
        tmp_unit = ''

        def get_suffix_set():
            suffix_sets = val_obj.options.suffix_sets
            suffix_sets_str = str(suffix_sets)
            try:
                return self._suffixes[suffix_sets_str]
            except KeyError:
                tmp_suffix_sets = {}
                for suf_set in suffix_sets:
                    for suf_key, suf_list in self._suffix_sets[suf_set].items():
                        for suf_alias in suf_list:
                            tmp_suffix_sets[suf_alias] = (suf_key, slice(0, (len(suf_alias)*-1), None), slice((len(suf_alias)*-1), None, None))

                self._suffixes[suffix_sets_str] = tmp_suffix_sets
            return tmp_suffix_sets

        if isinstance(value, str):

            if value[0] == '-':
                tmp_value = '-'
                split_loc = 1
            else:
                tmp_value = ''
                split_loc = 0

            while value[split_loc].isdecimal() or value[split_loc] == '.':
                tmp_value += value[split_loc]
                split_loc += 1
                if split_loc == len(value):
                    break
            tmp_unit = value[split_loc:].strip(' -')

            try:
                val_obj.value = int(tmp_value)
            except ValueError:
                try:
                    val_obj.value = float(tmp_value)
                except ValueError:
                    raise AttributeError('%s could not be converted to a numeric value (from %s)' % (tmp_value, value))

        if tmp_unit == '' and isinstance(val_obj.value, (int, float)):
            tmp_unit = self._default_unit

        if val_obj.unit is None:
            val_obj.unit = tmp_unit

        tmp_suffix = ''
        for suffix_alias, suffix_key in get_suffix_set().items():
            if val_obj.unit[suffix_key[2]] == suffix_alias:
                tmp_suffix = suffix_key[0]
                val_obj.unit = val_obj.unit[suffix_key[1]]
                break

        if val_obj.suffix is None and tmp_suffix is not '':
            val_obj.suffix = tmp_suffix

        if val_obj.unit == '' or val_obj.unit is None:
            if self._default_unit is not None:
                val_obj.unit = self._default_unit
            else:
                raise AttributeError('Could not parse unit out of %s and no unit passed' % value)

    def __call__(self, value=None, **options):
        """

        :param value:
        :keyword unit:
        :keyword suffix:
        :keyword return_unit:
        :keyword normalize:
        :keyword unitset:
        :keyword limit_to
        :keyword suffix_set
        :keyword use_aliases
        :keyword use_long_names
        :return:
        """


        if isinstance(value, DataSizeObject):
            val_obj = value
        else:
            val_obj = DataSizeObject(self, value=value)

        if options:
            while options:
                key, key_val = options.popitem()
                if hasattr(val_obj, key):
                    setattr(val_obj, key, key_val)
                else:
                    key = '_'+key
                    setattr(val_obj.options, key, key_val)

        if val_obj.value is not None:
            self._parse_item(val_obj)

        self._fix_units(val_obj)

        if val_obj.options.return_unit is not None:
            val_obj.value = self.convert(val_obj.value, from_unit=val_obj.unit, to_unit=val_obj.options.return_unit)

        if val_obj.options._normalize:
            self.normalize(val_obj)

        return val_obj



class DataSizeObject(object):
    # __slots__ = ['value', 'unit', 'suffix', 'unitset', 'options', 'initial_value', 'initial_unit']

    def __init__(self,
                 calculator=None,
                 value=None,
                 unit=None,
                 suffix=None,
                 unitset=None,
                 **kwargs):
        self._dsc = calculator or data_size_calculator
        self.value = value
        self.unit = unit
        self.suffix = suffix
        self.unitset = unitset or calculator._default_unitset

        self._initial_unit = unit
        self._initial_value = value

        self._option_manager = DataSizeOptions(self, **kwargs)

    def valid_units(self):
        if self.unit is not None:
            if not self._dsc._validate_unit(self.unit, self.options.limit_to):
                return False
        if hasattr(self.options, '_return_unit') and self.options.return_unit is not None:
            if not self._dsc._validate_unit(self.options.return_unit, self.options.limit_to):
                return False
        return True

    @property
    def options(self):
        return self._option_manager

    def __str__(self):
        suffix = self.suffix or ''
        tmp_ret = '%s %s%s' % (self.value, self.unit, suffix)
        return tmp_ret

    def __repr__(self):
        tmp_cfg = 'unitset: %s / options: %r' % (self.unitset, self.options)
        return 'DataSizeObject(%s) = %s' % (tmp_cfg, str(self))

class DataSizeCalculator(object):
    DECIMAL_BYTE = 'decimal-byte'
    DECIMAL_BIT = 'decimal-bit'
    BINARY_BYTE = 'binary-byte'
    BINARY_BIT = 'binary-bit'
    BIT = 'bit'
    BYTE = 'byte'
    BINARY = 'binary'
    DECIMAL = 'decimal'

    """
    This object is intended to be instantiated once per app, then called by
    the helper...  this will force the harder calculations to happen just
    once and be cached during the duration of the app.
    """

    def __init__(self,

                 default_limit_to=None,
                 default_unitset=None,
                 default_unit='B',

                 default_suffix_sets='network',
                 extra_suffixes=None,

                 default_use_aliases=True,
                 default_use_long_names=True,
                 extra_aliases=None,
                 fallback_unitset=DEC_BYT,
                 cache_compiled_lookups=True,

                 ):
        """

        :param default_limit_to: any of the extended unitsets
        :param default_alias_sets: any valid alias_set_names or objects
        :param default_suffix_sets: currently only ['network'|None]
        :param extra_aliases: format of: {'<unit short name>': ['<alias_name>', '<alias_name>'...]}
        :param extra_suffixes: format of ['suffix valid use': ['suffix', 'suffix', ...]}

        :param cache_compiled_lookups:
        :return:
        """

        self._cache_compiled_lookups = cache_compiled_lookups

        self._default_use_aliases = default_use_aliases
        self._default_use_long_names = default_use_long_names
        self._extra_aliases = extra_aliases

        self._default_suffix_sets = default_suffix_sets

        self._default_unit = default_unit
        self._default_unitset = default_unitset
        self._default_limit_to = default_limit_to
        self._fallback_unitset = fallback_unitset

        self._has_extra_aliases = extra_aliases is not None

        self._base_units = {}
        self._unit_lists = {}
        self._suffixes = {}
        # self._alias_unit_lists = {}
        self._suffix_sets = SUFFIX_SETS.copy()

        if extra_suffixes is not None:
            self._suffix_sets.update(extra_suffixes)

        self._unitsets = {
            DEC_BIT: [('b', 1)],
            DEC_BYT: [('B', 1)],
            BIN_BIT: [('b', 1)],
            BIN_BYT: [('B', 1)]}

        self._make_initial()

    def _make_initial(self):
        for unit_key, unit_info in BASEUNITS.items():

            for us in UNITSET_NAMES:

                us_info = UNITSET_INFO[us]

                unit_short_name = make_unit_name(unit_key, us)
                unit_long_name = make_unit_name(unit_key, us, long=True)

                self._base_units[unit_short_name] = {}
                base_rec = self._base_units[unit_short_name]

                base_rec['base_key'] = unit_key
                base_rec['short'] = {}
                base_rec['long'] = {}
                base_rec['short']['name'] = unit_short_name
                base_rec['long']['name'] = unit_long_name

                if unit_key == 'B':
                    if BYT in us:
                        base_rec['unitset'] = BYT
                    else:
                        base_rec['unitset'] = BIT
                else:
                    base_rec['unitset'] = us

                base_rec[BIN] = us_info['bd'] == BIN or unit_key.lower() == 'b'
                base_rec[DEC] = us_info['bd'] == DEC or unit_key.lower() == 'b'
                base_rec[BIT] = us_info['bb'] == BIT or unit_key == 'b'
                base_rec[BYT] = us_info['bb'] == BYT or unit_key == 'B'

                base_rec['conversions'] = {}
                base_rec['conversions'][BIN] = make_unit_name(unit_key, merge_ext_unitsets(BIN, us, force_a=True))
                base_rec['conversions'][DEC] = make_unit_name(unit_key, merge_ext_unitsets(DEC, us, force_a=True))
                base_rec['conversions'][BIT] = make_unit_name(unit_key, merge_ext_unitsets(BIT, us, force_a=True))
                base_rec['conversions'][BYT] = make_unit_name(unit_key, merge_ext_unitsets(BYT, us, force_a=True))
                base_rec['conversions'][opposite_unitset(us)] = make_unit_name(unit_key, opposite_unitset(us))

                unit_to_b_mult = ((us_info['power'] ** unit_info['cm']) * us_info['mult'])

                self._unitsets[us].append((unit_short_name, unit_to_b_mult))

                base_rec['to'] = {}
                base_rec['to']['b'] = unit_to_b_mult

                '''
                self._unit_list['base'][unit_short_name] = unit_short_name

                if self._include_long_names:
                    self._unit_list['base'][unit_long_name] = unit_short_name
                    self._unit_list['base'][unit_long_name.capitalize()] = unit_short_name
                '''

        for item in self._unitsets.values():
            item.sort(key=lambda k: k[1])

    def _get_limit_to_list(self, limit_to, use_aliases=False, use_long_names=True, unitset=None):

        alias_set_name = str(limit_to)

        if use_aliases:
            alias_set_name += 'UA=Y'
            if use_long_names:
                alias_set_name += ':ULN=Y'
            if unitset is not None:
                alias_set_name += ':U='+unitset

        if self._cache_compiled_lookups:
            try:
                return self._unit_lists[alias_set_name]
            except KeyError:
                pass

        tmp_alias_set = {}

        for u in self._base_units.values():
            short_name = u['short']['name']
            if limit_to is None:
                tmp_alias_set[short_name] = short_name
            elif u['base_key'] == 'B' and u['unitset'] in limit_to:
                tmp_alias_set[short_name] = short_name
            elif limit_to in u['unitset']:
                tmp_alias_set[short_name] = short_name

        if use_aliases:
            if use_long_names:
                tmp_ln_set = {}
                for unit in tmp_alias_set:
                    item = self._base_units[unit]
                    tmp_long_name = item['long']['name']
                    short_name = item['short']['name']

                    tmp_alias = tmp_long_name
                    tmp_ln_set[tmp_alias] = short_name
                    tmp_ln_set[tmp_alias+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')+'s'] = short_name

                    tmp_alias = tmp_long_name.capitalize()
                    tmp_ln_set[tmp_alias] = short_name
                    tmp_ln_set[tmp_alias+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')] = short_name
                    tmp_ln_set[tmp_alias.replace('byte', 'Byte')+'s'] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')] = short_name
                    tmp_ln_set[tmp_alias.replace('bit', 'Bit')+'s'] = short_name

                tmp_alias_set.update(tmp_ln_set)
            if self._has_extra_aliases:
                for key, item in self._extra_aliases.items():
                    if isinstance(item, str):
                        item = [item]
                    for alias in item:
                        tmp_alias_set[alias] = key

            if unitset is not None:

                tmp_alias_set['Mg'] = make_unit_name('M', unitset)
                tmp_alias_set['Meg'] = make_unit_name('M', unitset)
                tmp_alias_set['Gig'] = make_unit_name('G', unitset)

                for key, item in BASEUNITS.items():
                    short_name = make_unit_name(key, unitset)
                    tmp_alias_set[key] = short_name                       # ex: "M"
                    tmp_alias_set[key.lower()] = short_name               # ex: "m"

                tmp_case_set = {}
                for alias, key in tmp_alias_set.items():
                    alias_len = len(alias)
                    if alias == 'B':
                        if BIT not in unitset:
                            tmp_case_set['b'] = key
                    elif alias == 'b':
                        if BYT not in unitset:
                            tmp_case_set['B'] = key
                    elif 1 < alias_len < 4:
                        tmp_alias = alias[0].lower()+alias[1:]
                        tmp_case_set[tmp_alias] = key
                tmp_alias_set.update(tmp_case_set)

        if self._cache_compiled_lookups:
            self._unit_lists[alias_set_name] = tmp_alias_set

        return tmp_alias_set

    def _validate_unit(self, unit, limit_to):
        return unit in self._get_limit_to_list(limit_to=limit_to)

    def _fix_units(self, val_obj):

        if val_obj.valid_units():
            return

        unit_fixed = False
        return_fixed = val_obj.options.return_unit is None

        def try_fix(unit_fixed, return_fixed):
            tmp_unit_list = self._get_limit_to_list(
                limit_to=val_obj.options.limit_to,
                use_aliases=val_obj.options.use_aliases,
                use_long_names=val_obj.options.use_long_names,
                unitset=val_obj.unitset)

            if val_obj.unit in tmp_unit_list:
                val_obj.unit = tmp_unit_list[val_obj.unit]
                unit_fixed = True

            if val_obj.options.return_unit is not None:
                if val_obj.options._return_unit in tmp_unit_list:
                    val_obj.options._return_unit = tmp_unit_list[val_obj.options._return_unit]
                    return_fixed = True

            return unit_fixed, return_fixed



        unit_fixed, return_fixed = try_fix(unit_fixed, return_fixed)

        if unit_fixed and return_fixed:
            self._set_unitset(val_obj)
            return

        self._set_unitset(val_obj)

        unit_fixed, return_fixed = try_fix(unit_fixed, return_fixed)


        if not unit_fixed:
            raise AttributeError('Could not determine what units of measure %s is.' % val_obj.unit)
        if not return_fixed:
            raise AttributeError('Could not determine what units of measure %s is.' % val_obj.options.return_unit)

        return


    def _get_mult(self, from_unit, to_unit):
        tmp_from = self._base_units[from_unit]['to']
        try:
            return tmp_from[to_unit]
        except KeyError:
            tmp_from_bits = self._get_mult(from_unit, 'b')
            tmp_to_bits = self._get_mult(to_unit, 'b')
            tmp_from[to_unit] = tmp_from_bits / tmp_to_bits
            return tmp_from[to_unit]

    def _set_unitset(self, val_obj):

        if val_obj.unitset is not None:
            return

        def try_lookup(unit):
            unit_info = self._base_units[unit]
            if unit_info['base_key'] == 'B':
                return merge_ext_unitsets(unit_info['unitset'], self._default_unitset, force_a=True)
            else:
                return unit_info['unitset']

        if val_obj.unit is not None:
            try:
                val_obj.unitset = try_lookup(val_obj.unit)
                return
            except KeyError:
                if val_obj.options.return_unit is not None:
                    try:
                        val_obj.unitset = try_lookup(val_obj.options.return_unit)
                        return
                    except KeyError:
                        pass

        if val_obj.options.limit_to in UNITSET_NAMES:
            val_obj.unitset = val_obj.options.limit_to
            return

        if self._default_unitset is not None:
            val_obj.unitset = self._fallback_unitset
            return

        raise AttributeError('Unitset not detectable for %s' % val_obj)

    def convert(self, value, from_unit=None, to_unit='b'):
        tmp_value = value * self._get_mult(from_unit, to_unit)
        return tmp_value

    def normalize(self, val_obj):
        if val_obj.unitset is None:
            raise AttributeError('Unitset must be set in order to normalize information')

        base_value = self.convert(val_obj)
        norm_unit = 'b'
        for item in self._unitsets[val_obj.unitset]:
            if base_value.value < item[1]:
                break
            norm_unit = item[0]

        val_obj.value = self.convert(base_value, to_unit=norm_unit)
        val_obj.unit = norm_unit

    def _parse_item(self, val_obj):

        value = val_obj.value
        # suffix_sets = val_obj.options.suffix_sets
        tmp_unit = ''

        def get_suffix_set():
            suffix_sets = val_obj.options.suffix_sets
            suffix_sets_str = str(suffix_sets)
            try:
                return self._suffixes[suffix_sets_str]
            except KeyError:
                tmp_suffix_sets = {}
                for suf_set in suffix_sets:
                    for suf_key, suf_list in self._suffix_sets[suf_set].items():
                        for suf_alias in suf_list:
                            tmp_suffix_sets[suf_alias] = (suf_key, slice(0, (len(suf_alias)*-1), None), slice((len(suf_alias)*-1), None, None))

                self._suffixes[suffix_sets_str] = tmp_suffix_sets
            return tmp_suffix_sets

        if isinstance(value, str):

            if value[0] == '-':
                tmp_value = '-'
                split_loc = 1
            else:
                tmp_value = ''
                split_loc = 0

            while value[split_loc].isdecimal() or value[split_loc] == '.':
                tmp_value += value[split_loc]
                split_loc += 1
                if split_loc == len(value):
                    break
            tmp_unit = value[split_loc:].strip(' -')

            try:
                val_obj.value = int(tmp_value)
            except ValueError:
                try:
                    val_obj.value = float(tmp_value)
                except ValueError:
                    raise AttributeError('%s could not be converted to a numeric value (from %s)' % (tmp_value, value))

        if tmp_unit == '' and isinstance(val_obj.value, (int, float)):
            tmp_unit = self._default_unit

        if val_obj.unit is None:
            val_obj.unit = tmp_unit

        tmp_suffix = ''
        for suffix_alias, suffix_key in get_suffix_set().items():
            if val_obj.unit[suffix_key[2]] == suffix_alias:
                tmp_suffix = suffix_key[0]
                val_obj.unit = val_obj.unit[suffix_key[1]]
                break

        if val_obj.suffix is None and tmp_suffix is not '':
            val_obj.suffix = tmp_suffix

        if val_obj.unit == '' or val_obj.unit is None:
            if self._default_unit is not None:
                val_obj.unit = self._default_unit
            else:
                raise AttributeError('Could not parse unit out of %s and no unit passed' % value)

    def __call__(self, value=None, **options):
        """

        :param value:
        :keyword unit:
        :keyword suffix:
        :keyword return_unit:
        :keyword normalize:
        :keyword unitset:
        :keyword limit_to
        :keyword suffix_set
        :keyword use_aliases
        :keyword use_long_names
        :return:
        """


        if isinstance(value, DataSizeObject):
            val_obj = value
        else:
            val_obj = DataSizeObject(self, value=value)

        if options:
            while options:
                key, key_val = options.popitem()
                if hasattr(val_obj, key):
                    setattr(val_obj, key, key_val)
                else:
                    key = '_'+key
                    setattr(val_obj.options, key, key_val)

        if val_obj.value is not None:
            self._parse_item(val_obj)

        self._fix_units(val_obj)

        if val_obj.options.return_unit is not None:
            val_obj.value = self.convert(val_obj.value, from_unit=val_obj.unit, to_unit=val_obj.options.return_unit)

        if val_obj.options._normalize:
            self.normalize(val_obj)

        return val_obj

data_size_calculator = DataSizeCalculator()
