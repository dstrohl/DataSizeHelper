from copy import copy
import math
from bytes_helper_lookups import *
import logging

log = logging.getLogger(__name__)


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
                 default_force_as=None, default_assumptions='decimal-byte', default_suffix_sets='network',
                 extra_forces=None, extra_assumptions=None, extra_suffixes=None,
                 cache_compiled_lookups=True, include_long_names=True):
        """

        :param default_force_as:
        :param default_assumptions:
        :param default_suffix_sets:
        :param extra_forces:
        :param extra_assumptions:
        :param extra_suffixes:
        :param cache_compiled_lookups:
        :param include_long_names:
        :return:
        """

        self._cache_compiled_lookups = cache_compiled_lookups

        self._include_long_names = include_long_names
        self._extra_forces = extra_forces
        self._extra_assumptions = extra_assumptions
        self._extra_suffixes = extra_suffixes

        self._default_suffix_sets = default_suffix_sets
        self._default_assumptions = default_assumptions
        self._default_force_as = default_force_as

        self._has_extra_suffixes = extra_suffixes is not None
        self._has_extra_forces = extra_forces is not None
        self._has_extra_assumptions = extra_assumptions is not None

        # self._debug = debug
        self._from_to = {}
        self._aliases = {'base': {'b': 'b', 'B': 'B'}}
        self._assumtions = {}
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
            unit_info['unitsets'] = {}
            unit_unitsets = unit_info['unitsets']

            for us in UNITSET_NAMES:
                unit_unitsets[us] = {}
                us_info = UNITSET_INFO[us]

                if us_info['bd'] == 'binary':
                    unit_short_name = unit_info['bsn']+us_info['s_ext']
                    unit_long_name = unit_info['bln']+us_info['l_ext']
                else:
                    unit_short_name = unit_info['dsn']+us_info['s_ext']
                    unit_long_name = unit_info['dln']+us_info['l_ext']

                unit_unitsets[us]['short'] = unit_short_name
                unit_unitsets[us]['long'] = unit_long_name

                unit_to_b_mult = ((us_info['power'] ** unit_info['cm']) * us_info['mult'])

                self._unitsets[us].append((unit_short_name, unit_to_b_mult))

                self._from_to[unit_short_name] = dict(
                    to={'b': unit_to_b_mult},
                )
                self._aliases['base'][unit_short_name] = unit_short_name
                if self._include_long_names:
                    self._aliases['base'][unit_long_name] = unit_short_name
                    self._aliases['base'][unit_long_name.capitalize()] = unit_short_name

        for item in self._unitsets.values():
            item.sort(key=lambda k: k[1])

    def _make_unit(self, unit, assumption_set=None, force_as=None):
        return self._get_aliases(assumption_set, force_as)[unit]

    def _get_aliases(self, assumption_set=None, force_as=None):

        if self._cache_compiled_lookups:
            alias_set = str(assumption_set)+'.'+str(force_as)
            try:
                return self._aliases[alias_set]
            except KeyError:
                pass

        use_ass = self._use_assumption_set(assumption_set)
        use_fs = self._use_force_as_set(force_as)

        if not use_ass and not use_fs:
            return self._aliases['base']

        if use_ass:
            tmp_alias_dict = self._get_assumption_set(assumption_set)
        else:
            tmp_alias_dict = {}

        tmp_alias_dict.update(self._aliases['base'])

        if use_fs:
            tmp_forces = self._get_forces(force_as)
            for key, item in tmp_forces.items():
                if item is None:
                    del tmp_alias_dict[key]
                else:
                    tmp_alias_dict[key] = item

        if self._cache_compiled_lookups:
            self._aliases[alias_set] = tmp_alias_dict

        return tmp_alias_dict

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

    def _use_force_as_set(self, force_as=None):
        if self._default_force_as is not None or self._has_extra_forces:
            return True
        if force_as is None:
            return False
        if force_as in FORCE_AS_NAMES:
            return True
        else:
            return False

    def _get_forces(self, forcecode=None):
        forcecode = forcecode or self._default_force_as
        if forcecode is None and self._has_extra_forces:
            forcecode = '_default_'

        try:
            return self._forces[forcecode]
        except KeyError:
            forces = {}
            if forcecode != '_default_':
                for key, item in BASEUNITS.items():
                    if key == 'B':
                        if 'bit' in forcecode:
                            forces['B'] = 'b'
                            forces['b'] = 'b'
                        elif 'byte' in forcecode:
                            forces['B'] = 'B'
                            forces['b'] = 'B'
                        else:
                            forces['B'] = 'B'
                            forces['b'] = 'b'
                    else:
                        for unitset, info in item['unitsets'].items():

                            if 'decimal' in forcecode and 'binary' in unitset:
                                forces[info['short']] = None
                            else:
                                new_unitset = copy(unitset)

                                if 'binary' in forcecode and 'decimal' in unitset:
                                    new_unitset = new_unitset.replace('decimal', 'binary')

                                if 'bit' in forcecode:
                                    new_unitset = new_unitset.replace('byte', 'bit')
                                elif 'byte' in forcecode:
                                    new_unitset = new_unitset.replace('bit', 'byte')

                                forces[info['short']] = item['unitsets'][new_unitset]['short']

            if self._has_extra_forces:
                forces.update(self._extra_forces)

            self._forces[forcecode] = forces

        return self._forces[forcecode]

    def _use_assumption_set(self, assumption_set=None):
        if self._default_assumptions is not None or self._has_extra_assumptions:
            return True
        if assumption_set is None:
            return False
        if assumption_set in UNITSET_NAMES:
            return True
        else:
            return False

    def _get_assumption_set(self, assumption_set=None):
        assumption_set = assumption_set or self._default_assumptions
        if assumption_set is None and self._has_extra_assumptions:
            assumption_set = '_default_'

        try:
            return self._assumtions[assumption_set]
        except KeyError:
            if assumption_set != '_default_':
                self._assumtions[assumption_set] = {}
                assumes = self._assumtions[assumption_set]
                assumes['meg'] = BASEUNITS['M']['unitsets'][assumption_set]['short']
                assumes['gig'] = BASEUNITS['G']['unitsets'][assumption_set]['short']
                assumes['Meg'] = BASEUNITS['M']['unitsets'][assumption_set]['short']
                assumes['Gig'] = BASEUNITS['G']['unitsets'][assumption_set]['short']

                for key, item in BASEUNITS.items():
                    short_name = item['unitsets'][assumption_set]['short']
                    assumes[key] = short_name
                    assumes[key.lower()] = short_name
                    assumes[key.lower()+'b'] = short_name
                    assumes[key.lower()+'B'] = short_name
                    if len(short_name) == 3:
                        assumes[short_name.lower()] = short_name

            if self._has_extra_assumptions:
                self._assumtions[assumption_set].update(self._extra_assumptions)

        return self._assumtions[assumption_set]

    def _get_mult(self, from_unit, to_unit):
        tmp_from = self._from_to[self._make_unit(from_unit)]['to']
        to_unit = self._make_unit(to_unit)
        try:
            return tmp_from[self._make_unit(to_unit)]
        except KeyError:
            tmp_from_bits = self._get_mult(from_unit, 'b')
            tmp_to_bits = self._get_mult(to_unit, 'b')
            tmp_from[to_unit] = tmp_from_bits / tmp_to_bits
            return tmp_from[to_unit]

    def _merge_ext_unitsets(self, a, b, force_a=False):
        if a == b:
            return a
        if a is None:
            return b
        if b is None:
            return a

        out_a = {}
        out_b = {}

        if not force_a:

            out_a['bb'] = EXT_UNITSET_INFO[a]['bb'] or EXT_UNITSET_INFO[b]['bb']
            out_a['bd'] = EXT_UNITSET_INFO[a]['bd'] or EXT_UNITSET_INFO[b]['bd']
            out_b['bb'] = EXT_UNITSET_INFO[b]['bb'] or EXT_UNITSET_INFO[a]['bb']
            out_b['bd'] = EXT_UNITSET_INFO[b]['bd'] or EXT_UNITSET_INFO[a]['bd']

            if out_a['bb'] != out_b['bb'] or out_a['bd'] != out_b['bd']:
                raise AttributeError('unitsets contain unmergable attributes (%s / %s)' % (a, b))
        else:

            out_a['bb'] = EXT_UNITSET_INFO[a]['bb'] or EXT_UNITSET_INFO[b]['bb']
            out_a['bd'] = EXT_UNITSET_INFO[a]['bd'] or EXT_UNITSET_INFO[b]['bd']
        tmp_ret_list = []
        if out_a['bd'] is not None:
            tmp_ret_list.append(out_a['bd'])
        if out_a['bb'] is not None:
            tmp_ret_list.append(out_a['bb'])

        tmp_ret = '-'.join(tmp_ret_list)
        return tmp_ret

    def _detect_unitset(self, seed=None, force_unitset=None, prefer=None):

        tmp_ret_ds = self._merge_ext_unitsets(force_unitset, self._default_force_as)
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

            tmp_ret_ds = self._merge_ext_unitsets(tmp_ret_ds, seed_us, force_a=True)
            if tmp_ret_ds in UNITSET_NAMES:
                return tmp_ret_ds

        tmp_prefer_dataset = self._merge_ext_unitsets(prefer, self._default_assumptions, force_a=True)
        tmp_ret_ds = self._merge_ext_unitsets(tmp_ret_ds, tmp_prefer_dataset, force_a=True)

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
                 assumption_set=None, force_as=None, suffix_set=None, unitset=None):

        val_obj = self.parse_item(value, unit=unit, unitset=unitset, suffix=suffix_set,
                                  assumption_set=assumption_set, force_as=force_as)

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
