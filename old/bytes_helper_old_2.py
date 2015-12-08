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


    Alisa Sets:
        'common_names', (CN)
        'long_names', (LN)
        'case_changes' (CC)
        'convert_filtered_units' (CFU)


bin

dec-byt

bin-byt


'''


class BaseAliasGenerator(object):
    name = 'common_names'
    key = 'CN'

    def __init__(self, data_calc):
        self.dsc = data_calc

    def generate_aliases(self, unitset, alias_dict):
        raise NotImplementedError

    def __call__(self, unitset):
        return self.generate_aliases(unitset)


class CommonNameAliasGen(BaseAliasGenerator):
    name = 'common_names'
    key = 'CN'

    def generate_aliases(self, unitset, alias_dict):

        tmp_ret = {}
        tmp_ret['meg'] = make_unit_name('M', unitset)
        tmp_ret['mg'] = make_unit_name('M', unitset)
        tmp_ret['Mg'] = make_unit_name('M', unitset)
        tmp_ret['gig'] = make_unit_name('G', unitset)
        tmp_ret['Meg'] = make_unit_name('M', unitset)
        tmp_ret['Gig'] = make_unit_name('G', unitset)

        alias_dict.update(tmp_ret)


class WrongCaseAliasGen(BaseAliasGenerator):
    name = 'fix_case'
    key = 'FC'

    def generate_aliases(self, unitset, alias_dict):

        tmp_ret = {}
        for key, item in BASEUNITS.items():
            short_name = make_unit_name(key, unitset)
            tmp_ret[key] = short_name                       # ex: "M"
            tmp_ret[key.lower()] = short_name               # ex: "m"

        for alias, key in alias_dict.items():
            alias_len = len(alias)
            if alias == 'B':
                if BIT not in unitset:
                    tmp_ret['b'] = key
            elif alias == 'b':
                if BYT not in unitset:
                    tmp_ret['B'] = key
            elif alias_len == 2 or alias_len == 3:
                tmp_alias = alias[0].lower()+alias[1:]
                tmp_ret[tmp_alias] = key
            elif alias_len >= 3:
                tmp_alias = alias[0].upper()+alias[1:]
                tmp_ret[tmp_alias] = key

                tmp_alias = alias.replace('byte', 'Byte')
                tmp_ret[tmp_alias] = key

                tmp_alias = alias.replace('bit', 'Bit')
                tmp_ret[tmp_alias] = key

        alias_dict.update(tmp_ret)


class AddExtraAliases(BaseAliasGenerator):
    name = 'extra-aliases'
    key = 'EA'

    def generate_aliases(self, unitset, alias_dict):
        if self.dsc._has_extra_aliases:
            tmp_ret = {}
            for key, item in self.dsc._extra_aliases.items():
                if isinstance(item, str):
                    item = [item]
                for alias in item:
                    tmp_ret[alias] = key

            alias_dict.update(tmp_ret)


class AddLongNameAliases(BaseAliasGenerator):
    name = 'long_names'
    key = 'LN'

    def generate_aliases(self, unitset, alias_dict):
        tmp_ret = {}

        for item in self.dsc._get_filtered_units(unitset):
            tmp_ret[item['long']['name']] = item['short']['name']

        alias_dict.update(tmp_ret)


class DataSizeObject(object):
    __slots__ = ['value', 'unit', 'suffix', 'unitset']

    def __init__(self, value, unit, suffix=None, unitset=None):
        self.value = value
        self.unit = unit
        if suffix is None:
            self.suffix = ''
        else:
            self.suffix = suffix

        if unitset is None:
            self.unitset = ''
        else:
            self.unitset = unitset

    def __str__(self):
        tmp_ret = '%s %s%s' % (self.value, self.unit, self.suffix)
        if self.unitset != '':
            tmp_ret += ' [%s]' % self.unitset
        return tmp_ret

    def __repr__(self):
        return 'DataSizeObject(%s)' % str(self)

class DataSizeCalculator(object):
    """
    This object is intended to be instantiated once per app, then called by
    the helper...  this will force the harder calculations to happen just
    once and be cached during the duration of the app.
    """

    def __init__(self,
                 default_force_as=None, default_aliases='decimal-byte', default_suffix_sets='network',
                 limit_to_unitset=None, extra_forces=None, extra_aliases=None, extra_suffixes=None,
                 cache_compiled_lookups=True, include_long_names=True):
        """

        :param default_force_as: any of the extended unitsets
        :param default_aliases: any unitsets
        :param default_suffix_sets: currently only ['network'|None]
        :param extra_forces: format of: {'<valid unit>':'<forces to this unit>', ...}
        :param extra_aliases: format of: {'<unit short name>': ['<alias_name>', '<alias_name>'...]
        :param extra_suffixes: format of ['suffix', 'suffix', ...]

        :param cache_compiled_lookups:
        :param include_long_names:
        :return:
        """

        self._cache_compiled_lookups = cache_compiled_lookups

        self._include_long_names = include_long_names
        self._extra_forces = extra_forces
        self._extra_aliases = extra_aliases
        self._extra_suffixes = extra_suffixes

        self._limit_to_unitset = limit_to_unitset

        self._default_suffix_sets = default_suffix_sets
        self._default_aliases = default_aliases
        self._default_force_as = default_force_as

        self._has_extra_suffixes = extra_suffixes is not None
        self._has_extra_forces = extra_forces is not None
        self._has_extra_aliases = extra_aliases is not None

        # self._debug = debug
        self._base_units = {}
        self._unit_list = {'base': {'b': 'b', 'B': 'B'}}
        self._aliases = {}
        self._suffixes = {}
        self._forces = {}
        self._unitsets = {
            DEC_BIT: [('b', 1)],
            DEC_BYT: [('B', 1)],
            BIN_BIT: [('b', 1)],
            BIN_BYT: [('B', 1)]}

        self._make_initial()



    def _make_initial(self):
        for unit_key, unit_info in BASEUNITS.items():

            for us in UNITSET_NAMES:

                if self._limit_to_unitset is not None:
                    if us not in self._limit_to_unitset:
                        continue

                us_info = UNITSET_INFO[us]

                unit_short_name = make_unit_name(unit_key, us)
                unit_long_name = make_unit_name(unit_key, us, long=True)

                self._base_units[unit_short_name] = {}
                base_rec = self._base_units[unit_short_name]

                base_rec['base_key'] = unit_key
                base_rec['short'] = {}
                base_rec['long'] = {}
                base_rec['short']['name'] = unit_short_name
                base_rec['short']['aliases'] = []
                base_rec['long']['name'] = unit_long_name
                base_rec['long']['aliases'] = []
                base_rec['long']['aliases'].append(unit_long_name.capitalize())

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

    def _get_filtered_units(self, unitset=None):
        '''
        if unitset is not None:
            breakout_us = breakout_unitset(unitset)
        '''
        for u in self._base_units:
            if unitset is None:
                yield u
            elif u['basekey'] == 'B' and u['unitset'] in unitset:
                yield u
            elif unitset in u['unitset']:
                yield u


    def _make_for_unit_list(self, unit_rec, reference_key=None, inc_long=None, inc_aliases=True):
        reference_key = reference_key or unit_rec['short']['name']
        inc_long = inc_long or self._include_long_names
        tmp_ret = {}

        for sl in ('short', 'long'):
            if sl == 'long' and not inc_long:
                break
            tmp_ret[unit_rec[sl]['name']] = reference_key
            if inc_aliases:
                for a in unit_rec[sl]['aliases']:
                    tmp_ret[a] = reference_key
        return tmp_ret

    def _get_unit_list(self, force_set=None, alias_set=None):

        if self._cache_compiled_lookups:
            alias_set_name = 'F:%s.A:%s' % (str(force_set), str(alias_set))
            try:
                return self._unit_list[alias_set_name]
            except KeyError:
                pass

        tmp_alias_set = merge_ext_unitsets(alias_set, self._default_aliases, force_a=True)
        tmp_force_set = merge_ext_unitsets(force_set, self._default_force_as)

        if self._use_alias_set(tmp_alias_set):
            tmp_ret = self._get_alias_set(tmp_alias_set)
        else:
            tmp_ret = {}

        for unit in self._base_units.values():
            tmp_diff = diff_unitset(tmp_force_set, unit['unitset'])

            if tmp_diff is None:
                tmp_ret.update(self._make_for_unit_list(unit))
            else:
                tmp_ret.update(self._make_for_unit_list(unit, reference_key=unit['conversions'][tmp_diff]))

        if self._cache_compiled_lookups:
            self._unit_list[alias_set_name] = tmp_ret

        return tmp_ret

    def _make_unit(self, unit, alias_set=None, force_as=None):
        return self._get_unit_list(alias_set=alias_set, force_set=force_as)[unit]

    def _use_suffix_set(self, suffix_sets=None):
        if self._default_suffix_sets is not None or self._has_extra_suffixes:
            return True
        if suffix_sets is None:
            return False
        if suffix_sets in SUFFIX_SETS:
            return True
        else:
            return False

    def _get_suffix_set(self, suffix_sets=None):
        suffix_set = suffix_sets or self._default_suffix_sets

        if suffix_set is None and self._has_extra_suffixes:
            suffix_set = '_extra_only_'

        try:
            return self._suffixes[suffix_set]
        except KeyError:

            self._suffixes[suffix_set] = {}

            try:
                tmp_suffixes = SUFFIX_SETS[suffix_set]
            except KeyError:
                tmp_suffixes = {}

            if self._has_extra_suffixes:
                # self._suffixes[suffix_set].update(self._extra_suffixes)
                tmp_suffixes.update(self._extra_suffixes)

            for sk, sl in tmp_suffixes.items():
                for sa in sl:
                    self._suffixes[suffix_set][sa] = (sk, slice(0, (len(sa)*-1), None), slice((len(sa)*-1), None, None))

        return self._suffixes[suffix_set]

    def _use_alias_set(self, alias_set=None):
        if self._default_aliases is not None or self._has_extra_aliases:
            return True
        if alias_set is None:
            return False
        if alias_set in UNITSET_NAMES:
            return True
        else:
            return False

    def _get_alias_set(self, alias_set=None):

        if alias_set is None and self._has_extra_aliases:
            alias_set = '_default_'

        try:
            return self._aliases[alias_set]
        except KeyError:
            pass

        self._aliases[alias_set] = {}
        assumes = self._aliases[alias_set]

        # assumes = {}
        if alias_set != '_default_':
            assumes['meg'] = make_unit_name('M', alias_set)
            assumes['mg'] = make_unit_name('M', alias_set)
            assumes['Mg'] = make_unit_name('M', alias_set)
            assumes['gig'] = make_unit_name('G', alias_set)
            assumes['Meg'] = make_unit_name('M', alias_set)
            assumes['Gig'] = make_unit_name('G', alias_set)

            for key, item in BASEUNITS.items():
                short_name = make_unit_name(key, alias_set)
                assumes[key] = short_name                       # ex: "M"
                assumes[key.lower()] = short_name               # ex: "mb"
                assumes[key.lower()+'b'] = short_name           # ex: "mb" (for "Mb")
                assumes[key.lower()+'B'] = short_name           # ex: "mB" (for "MB")
                if len(short_name) == 3:
                    assumes[short_name.lower()] = short_name    # ex: "mib" (for "MiB")

        if self._has_extra_aliases:
            for key, item in self._extra_aliases.items():
                if isinstance(item, str):
                    item = [item]
                for alias in item:
                    assumes[alias] = key

        return assumes

    def _get_mult(self, from_unit, to_unit):
        tmp_from = self._base_units[self._make_unit(from_unit)]['to']
        to_unit = self._make_unit(to_unit)
        try:
            return tmp_from[self._make_unit(to_unit)]
        except KeyError:
            tmp_from_bits = self._get_mult(from_unit, 'b')
            tmp_to_bits = self._get_mult(to_unit, 'b')
            tmp_from[to_unit] = tmp_from_bits / tmp_to_bits
            return tmp_from[to_unit]


    def _detect_unitset(self, seed=None, force_unitset=None, prefer=None):

        tmp_ret_ds = merge_ext_unitsets(force_unitset, self._default_force_as)
        if tmp_ret_ds in UNITSET_NAMES:
            return tmp_ret_ds

        if seed is not None:
            seed = self._make_unit(seed)

            if len(seed) == 3:
                if seed[2] == 'b':
                    seed_us = BIN_BIT
                else:
                    seed_us = BIN_BYT
            elif len(seed) == 2:
                if seed[1] == 'b':
                    seed_us = DEC_BIT
                else:
                    seed_us = DEC_BYT
            elif len(seed) == 1:
                if seed == 'b':
                    seed_us = BIT
                else:
                    seed_us = BYT
            else:
                seed_us = None

            tmp_ret_ds = merge_ext_unitsets(tmp_ret_ds, seed_us, force_a=True)
            if tmp_ret_ds in UNITSET_NAMES:
                return tmp_ret_ds

        tmp_prefer_dataset = merge_ext_unitsets(prefer, self._default_aliases, force_a=True)
        tmp_ret_ds = merge_ext_unitsets(tmp_ret_ds, tmp_prefer_dataset, force_a=True)

        if tmp_ret_ds in UNITSET_NAMES:
            return tmp_ret_ds

        return DEFAULT_UNITSETS[tmp_ret_ds]

    def convert(self, value, from_unit=None, to_unit='b', **parse_args):
        val_obj = self.parse_item(value, unit=from_unit, **parse_args)
        val_obj.value = val_obj.value * self._get_mult(val_obj.unit, to_unit)
        val_obj.unit = to_unit
        return val_obj

    def parse_item(self, value, unit=None, suffix=None, unitset=None, fix_units=True, **fix_unit_args):

        if isinstance(value, DataSizeObject):
            return value

        if isinstance(value, (int, float)) and unit is not None and suffix is not None:
            return DataSizeObject(value=value, unit=unit, suffix=suffix, unitset=unitset)

        tmp_unit = None
        tmp_value = value
        tmp_suffix = suffix

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
                tmp_value = int(tmp_value)
            except ValueError:
                try:
                    tmp_value = float(tmp_value)
                except ValueError:
                    raise AttributeError('%s could not be converted to a numeric value (from %s)' % (tmp_value, value))

            if self._use_suffix_set():
                tmp_suffix = ''
                for suffix_alias, suffix_key in self._get_suffix_set().items():
                    if tmp_unit[suffix_key[2]] == suffix_alias:
                        tmp_suffix = suffix_key[0]
                        tmp_unit = tmp_unit[suffix_key[1]]
                        break

        if unit is not None:
            tmp_unit = unit

        if tmp_unit == '' or tmp_unit is None:
            raise AttributeError('Could not parse unit out of %s and no unit passed' % value)

        if suffix is not None:
            suf_len = len(suffix)
            tmp_suffix = suffix
            if tmp_unit[-suf_len:] == suffix:
                tmp_unit = tmp_unit[:-suf_len]

        if fix_units:
            tmp_unit = self._make_unit(tmp_unit, **fix_unit_args)

        return DataSizeObject(value=tmp_value, unit=tmp_unit, suffix=tmp_suffix, unitset=unitset)

    def normalize(self, value, unit=None, unitset=None):
        val_obj = self.parse_item(value, unit=unit, unitset=unitset)
        if val_obj.unitset == '' or val_obj.unitset is None:
            val_obj.unitset = self._detect_unitset(seed=val_obj.unit)

        base_value = self.convert(val_obj)
        norm_unit = 'b'
        for item in self._unitsets[val_obj.unitset]:
            if base_value.value < item[1]:
                break
            norm_unit = item[0]

        val_obj = self.convert(base_value, to_unit=norm_unit)
        return val_obj

    def __call__(self, value, unit=None, return_as=None, normalize=False,
                 alias_set=None, force_as=None, suffix_set=None, unitset=None):

        val_obj = self.parse_item(value, unit=unit, unitset=unitset, suffix=suffix_set,
                                  alias_set=alias_set, force_as=force_as)

        if return_as is not None:
            val_obj = self.convert(val_obj, to_unit=return_as)

        if normalize:
            val_obj = self.normalize(val_obj)

        return val_obj

data_size_calculator = DataSizeCalculator()

class DataSizeHelper(object):
    _value = 0
    _to_storage_mult = 0
    _detection = 'strict'
    _unit_calc = CONVERSION_UNITS
    _default_units = 'B'
    _storage_units = 'b'
    _assumed_suffix = ''
    _assumed_bin_suffix = ''
    _seed_units = 'b'
    _is_seed = True
    _str_format = '{value} {units}'

    _normalize_lookup_cache = None

    def __init__(self,
                 initial_value=0,
                 default_units='B',
                 storage_units='b',
                 unit_detection='strict'):
        """

        :param initial_value:
        :param default_units: if just a number is passed, what do we assume it is
        :param storage_units: normally everything is stored in bytes, however when working with very large numbers
            it may be easier to store data in a different unit.
        :param unit_base: ['decimal-bits'|'decimal-bytes'|'binary-bits'|'binary-bytes']
            if the unit is passed and is not determinable (i.e. "M"), how do we determine what it is:

            * strict: (default) Will raise an error if undetermined strings are passed.
            * bits: will assume "M" = "Mb", "mb" = "Mb"
            * bytes: will assume "M" = "MB", "mb" = "MB", "Mb" = "Mb"
            * binary-bits: will assume "M" = "Mib", "mb" = "MiB"
            * binary-bytes: will assume "M" = "MiB",

            if not in strict mode, 2 chars are passed, and all of the letters are L/C, we will drop the second letter
              and parse as above.

            * strict mode = true will force any passed values to be evaluated based on their
            * *-bits will assume that any units are bits

            assume_bytes = True
            assume_decimal = True
            strict = True

        :return:
        """
        self.set_detection(unit_detection)
        self.set_default(default_units)
        self.set_storage(storage_units)

        self.set(initial_value)

    def _detect_dataset(self, seed=None):
        """
        determines how to determine closest unit:

        if seed is passed:
            if seed == valid set, return that

        if no seed and detect_method is not 'strict'
            use detect method

        if detect_method is 'strict' or seed is passed:
            if default unit or seed is not 'b'|'B'
                use default unit or seed
            else
                b = decimal-bits
                B = decimal-bytes

        :param seed:
        :return:
        """

        if seed is not None and seed in ('binary-bits', 'binary-bytes', 'decimal-bits', 'decimal-bytes'):
            return seed

        if seed is None:
            if self._detection in ('binary-bits', 'binary-bytes'):
                return self._detection
            elif self._detection in ('bits', 'bytes'):
                return 'decimal-'+self._detection

        return DATASETS[seed or self._default_units]

    '''
    @property
    def _get_normalize_lookup(self):
        rep_units = self._detect_dataset()

        for unit in UNITSETS[rep_units]:
            self._normalize_lookup_cache.append(unit, CONVERSIONUNITS[unit])
        return self._normalize_lookup_cache

    '''

    def _get_storage(self, value, units=None):

        if issubclass(value.__class__, self.__class__):
            return value.get(units=self._default_units)

        value, units = self._parse_value(value, units)
        if self._is_seed:
            return value * self._unit_calc[units]
        else:
            return self.convert(value, units, self._storage_units)

    def set(self, value, units=None):
        self._value = self._get_storage(value, units=units)

    def get(self, units=None):
        units = self._get_units(units)

        if self._is_seed:
            return self._value / self._unit_calc[units]
        else:
            return self.convert(self._value, self._storage_units, units)

    def get_str(self, units=None):
        units = self._get_units(units)
        tmp_value = self.get(units)
        return self._str_format.format(value=tmp_value, units=units)

    def set_storage(self, units):
        if self._value != 0:
            self._value = self.convert(self._value, self._storage_units, units)
        self._storage_units = self._get_units(units, force_strict=True)
        self._is_seed = self._storage_units == self._seed_units
        return self

    def set_detection(self, method):
        self._detection = method
        if method == 'strict':
            self._assumed_suffix = ''
            self._assumed_bin_suffix = ''

        elif method == 'bits':
            self._assumed_suffix = 'b'
            self._assumed_bin_suffix = 'ib'

        elif method == 'bytes':
            self._assumed_suffix = 'B'
            self._assumed_bin_suffix = 'iB'

        elif method == 'binary-bits':
            self._assumed_suffix = 'ib'
            self._assumed_bin_suffix = 'ib'

        elif method == 'binary-bytes':
            self._assumed_suffix = 'iB'
            self._assumed_bin_suffix = 'iB'

        else:
            raise AttributeError('Invalid detection mode specified: %s' % method)

        return self

    def set_default(self, default):
        self._default_units = self._get_units(default, force_strict=True)
        return self

    def _get_units(self, str_in=None, force_strict=False):
        if str_in is None:
            return self._default_units

        if str_in in self._unit_calc:
            return str_in

        if self._detection == 'strict' or force_strict:
            raise AttributeError('Invalid unit type: %s' % str_in)

        if len(str_in) == 1:
            tmp_unit = str_in.upper() + self._assumed_suffix
        elif len(str_in) == 2:
            tmp_unit = str_in[0].upper() + self._assumed_suffix
        elif len(str_in) == 3:
            tmp_unit = str_in[0].upper() + self._assumed_bin_suffix
        else:
            tmp_unit = 'foo'

        if tmp_unit in self._unit_calc:
            return tmp_unit

        raise AttributeError('Invalid unit type: %s' % str_in)

    def _parse_value(self, value, units=None):
        if isinstance(value, (int, float)):
            tmp_value = value
            tmp_unit = units or self._default_units
        elif isinstance(value, str):
            tmp_value = ''
            tmp_unit = ''
            split_loc = 0
            while value[split_loc].isnumeric():
                tmp_value += value[split_loc]
                split_loc += 1
            tmp_unit = value[split_loc:]
            tmp_unit = self._get_units(tmp_unit.strip())
            try:
                tmp_value = int(tmp_value)
            except ValueError:
                tmp_value = float(tmp_value)
        return tmp_value, tmp_unit

    def _get_mult(self, from_unit, to_unit):
        return self._unit_calc[from_unit] / self._unit_calc[to_unit]

    def convert(self, value, from_unit, to_unit):
        return value * self._get_mult(from_unit, to_unit)

    def __call__(self, value=None, units=None):
        if value is None:
            return self.get(units)
        else:
            self.set(value, units)
            return self

    def __str__(self):
        return self.get_str()

    def __getattr__(self, item):
        return self.get(units=item)

    def __setattr__(self, key, value):
        if key in dir(self):
            super().__setattr__(key, value)
        else:
            self.set(value, key)

    # Comparison Magic Methods

    def _comp(self, other):
        return self._value - self._get_storage(other)

    def __eq__(self, other):
        return self._comp(other) == 0

    def __neq__(self, other):
        return self._comp(other) != 0

    def __lt__(self, other):
        return self._comp(other) < 0

    def __le__(self, other):
        return self._comp(other) <= 0

    def __gt__(self, other):
        return self._comp(other) > 0

    def __ge__(self, other):
        return self._comp(other) >= 0

    # Math Methods

    def __round__(self, n=None):
        tmp_num = self.get()
        return round(tmp_num, n)

    def __floor__(self):
        tmp_num = self.get()
        return math.floor(tmp_num)

    def __ceil__(self):
        tmp_num = self.get()
        return math.ceil(tmp_num)

    def __trunc__(self):
        tmp_num = self.get()
        return math.trunc(tmp_num)

    def _math_helper(self, other, operation, as_value=None):
        ret_class = issubclass(other.__class__, self.__class__)
        other_value = self._get_storage(other)

        if operation == 'add':
            new_value = self.get() + other_value
        elif operation == 'sub':
            new_value = self.get() - other_value
        elif operation == 'mul':
            new_value = self.get() * other_value
        elif operation == 'floordiv':
            new_value = self.get() // other_value
        elif operation == 'div':
            new_value = self.get() / other_value
        elif operation == 'mod':
            new_value = self.get() % other_value
        elif operation == 'pow':
            new_value = self.get() ** other_value
        elif operation == 'lshift':
            new_value = self.get() << other_value
        elif operation == 'rshift':
            new_value = self.get() >> other_value
        elif operation == 'and':
            new_value = self.get() % other_value
        elif operation == 'or':
            new_value = self.get() | other_value
        elif operation == 'xor':
            new_value = self.get() ^ other_value
        else:
            raise AttributeError('Invalid operaion: %s' % operation)

        if ret_class and not as_value:
            return self.__class__(
                initial_value=new_value,
                default_units=self._default_units,
                storage_units=self._storage_units,
                unit_detection=self._detection)
        else:
            return new_value

    def __add__(self, other):
        return self._math_helper(other, 'add')

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        self._value = self._math_helper(other, 'add')

    # --------------------------------------

    def __mul__(self, other):
        return self._math_helper(other, 'mul')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        self._value = self._math_helper(other, 'mul')

    # --------------------------------------

    def __floordiv__(self, other):
        return self._math_helper(other, 'floordiv')

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __ifloordiv__(self, other):
        self._value = self._math_helper(other, 'floordiv')

    # --------------------------------------

    def __div__(self, other):
        return self._math_helper(other, 'div')

    def __rdiv__(self, other):
        return self.__div__(other)

    def __idiv__(self, other):
        self._value = self._math_helper(other, 'div')

    # --------------------------------------

    def __mod__(self, other):
        return self._math_helper(other, 'mod')

    def __rmod__(self, other):
        return self.__mod__(other)

    def __imod__(self, other):
        self._value = self._math_helper(other, 'mod')

    # --------------------------------------

    def __pow__(self, other):
        return self._math_helper(other, 'pow')

    def __rpow__(self, other):
        return self.__pow__(other)

    def __ipow__(self, other):
        self._value = self._math_helper(other, 'pow')

    # --------------------------------------

    def __lshift__(self, other):
        return self._math_helper(other, 'lshift')

    def __rlshift__(self, other):
        return self.__lshift__(other)

    def __ilshift__(self, other):
        self._value = self._math_helper(other, 'lshift')

    # --------------------------------------

    def __rshift__(self, other):
        return self._math_helper(other, 'rshift')

    def __rrshift__(self, other):
        return self.__rshift__(other)

    def __irshift__(self, other):
        self._value = self._math_helper(other, 'rshift')

    # --------------------------------------

    def __and__(self, other):
        return self._math_helper(other, 'and')

    def __rand__(self, other):
        return self.__and__(other)

    def __iand__(self, other):
        self._value = self._math_helper(other, 'and')

    # --------------------------------------

    def __or__(self, other):
        return self._math_helper(other, 'or')

    def __ror__(self, other):
        return self.__or__(other)

    def __ior__(self, other):
        self._value = self._math_helper(other, 'or')

    # --------------------------------------

    def __xor__(self, other):
        return self._math_helper(other, 'xor')

    def __rxor__(self, other):
        return self.__xor__(other)

    def __ixor__(self, other):
        self._value = self._math_helper(other, 'xor')

    # Conversion Methods

    def __int__(self):
        return int(self.get())

    def __float__(self):
        return float(self.get())

    def __long__(self):
        return int(self.get())

    def __complex__(self):
        return complex(self.get())

    def __oct__(self):
        return oct(self.get())

    def __hex__(self):
        return hex(self.get())

    def __hash__(self):
        return hash(self.get())

    def __repr__(self):
        tmp_msg = 'DataBytesHelper: '+self.get_str()
        return tmp_msg
