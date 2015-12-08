from copy import copy
import math
from data_unit_calc import *
from data_unit_lookups import *
from data_base_units import *
from number_formatter import text_number_formatter
from decimal import Decimal, InvalidOperation

import locale
locale.setlocale(locale.LC_ALL, '')

"""

Custom Format Syntax:
{...:custom_format_spec}

Same as standard except for the [type] field, which is as follows:
    (separate keys with ':')

normalize to unitset keys:
    ("+" = use long names)
    bb = binary_byte
    bt = binary_bit
    db = decimal_byte
    dt = decimal_bit
    None = do not normalize
    n = normalize to default unitset

force to unit keys:
    use short names such as Mb, KiB, etc)
    None = use defined units
    "+" indicates to use long names

    if short names are used, long names can be identified by also passing a "D".

include suffix (if present):
    s = do not include suffix
    S = include suffix (default)

Pluralize (if needed for long names):
    l = do not pluralize
    L = pluralize (default)

Case (only for long names):
    c = lower
    C = proper (default)

examples:

initial value   format spec     final value
10 GB/s,        {:4.2:MB+} "10000.00 Megabytes/s"
10 GB/s,        {:<6:bb:S}         "10     Gb/s"
1 Kb/s,        {:bb:s:}         "0.195 Kb"
10 Gb/s,        {:+:c:l}        '10 gigabyte/s"


unit = the currently set unit for reporting.



        Custom Format Syntax (separate keys with ':'):

            [:unitset|:unit][+][:s|:S][:l|:L][:c|:C]

            Unitset or Unit:
                'bb': normalize to binary byte
                'bt': normalize to bin_bit
                'db': normalize to dec_byte
                'dt': normalize to dec_bit
                'n': normalize to defined unitset (if defined)
                <unit short name>: force to unit short name
                'd': use standard defined units
                None/Missing = do not normalize

            '+':
                Forces the use of long names (such as megabyte instead of Mb).

            's' or 'S':
                's': Do not include suffix
                'S': Include suffix ('/s') if defined [default]

            The following are only used if long names are used.
            'l' or 'L':
                'l': Do not pluralize.
                'L': pluralize if long names are used [default]

            'c' or 'C':
                'c': Only use lower case
                'C': Use proper case ('Megabyte') [default]

        examples (using 'MB' unit):

            * {:MB+} = "Megabytes/s"
            * {:bb:S} "
            * {:BB:s:}         "0.195 Kb"
            * {:D:c:l}        '10 gigabyte/s"



"""


class DataSizeHelper(object):
    """
    Provides an object that understands normal data units and can convert between them as needed.  In addition to the
    noted methods, you can also interact with this in the following ways:

    DataSizeHelper.<data_unit_short_name> = value
    DataSizeHelper.<data_unit_short_name>
    str(DataSizeHelper)
    DataSizeHelper + object
    DataSizeHelper += object
    DataSizeHelper > object
    '<format definition>'.format(DataSizeHelper)
    """
    _unit_manager = data_units
    _calculator = data_size_calculator
    _value = 0
    _unit = None
    _suffix = None
    _default_unit = 'B'
    _storage_unit = 'b'
    _unitset = None
    _str_format = 'd:s'
    _aliases = None
    _base_units = 'b'
    _tmp_unit = None
    _normalize_lookup_cache = None

    def __init__(self,
                 value=0,
                 unit=None,
                 suffix=None,
                 default_unit=None,
                 storage_unit='b',
                 unitset=None,
                 unit_manager=None,
                 calculator=None):
        """

        :param value: The value of the object
        :param unit: The unit for the object
        :param suffix: Any suffix ('/s' for example)
        :param default_unit: If just a number is passed, what unit do we assume it is
        :param storage_unit: Normally everything is stored in bits, however when working with very large numbers
            it may be easier to store data in a different unit.  if all units will be the same, this may reduce
            calculation time as well.
        :param unitset: the unitset may need to be passed if normalization is required and the system cannot
        automatically determine it.  (primarily if working with 'B' or 'b').
        :param unit_manager: if desired, allows overriding the unit manager which handles unit name detection and
        normalization
        :param calculator:  If desired, allows overriding the unit calculator which handles converting between units.
        """
        self._unit_manager = unit_manager or self._unit_manager
        self._calculator = calculator or self._calculator
        self._storage_unit = storage_unit
        self.suffix = suffix
        self.unit = unit or default_unit
        self._tmp_unit = unit
        self.value = value
        self._aliases = self._unit_manager.aliases()
        self.default_unit = default_unit or unit or self._default_unit
        self.unitset = unitset

    # <editor-fold desc=" ********************* Properties ****************************************">

    def _set_value(self, value):
        tmp_unit = self._tmp_unit or self._default_unit
        tmp_value, tmp_unit, tmp_suffix = self._parse_value(value, tmp_unit)
        self.unit = tmp_unit or self.unit
        self.suffix = tmp_suffix or self.suffix
        self._value = self._convert(tmp_value, from_unit=self.unit)
        self._tmp_unit = None

    def _get_value(self):
        return self._value

    value = property(fset=_set_value, fget=_get_value)

    def _set_unit(self, unit):
        unit, suffix = self._fix_unit(unit)
        self.suffix = suffix or self.suffix
        self._unit = unit

    def _get_unit(self):
        return self._unit

    unit = property(fset=_set_unit, fget=_get_unit)

    def _set_default_unit(self, unit, validate=False):
        if validate:
            unit, suffix = self._fix_unit(unit)
        self._default_unit = unit

    def _get_default_unit(self):
        return self._default_unit

    default_unit = property(fset=_set_default_unit, fget=_get_default_unit)


    def _set_suffix(self, suffix):
        self._suffix = suffix

    def _get_suffix(self):
        return self._suffix

    suffix = property(fset=_set_suffix, fget=_get_suffix)

    def set_unitset(self, unitset=None, fix_unit=False):
        if unitset is None:
            self._unitset = self._unit_info().full_unitset()
        else:
            if not self._unit_info().unitset_match(unitset):
                if fix_unit:
                    self.unit = self._unit_info().convert_unitset(unitset)
                else:
                    raise AttributeError('Default unit (%s) does not match unitset (%s)' % self.unit, unitset)
            self._unitset = unitset
        return self

    def _get_unitset(self):
        if self._unitset is None:
            self.set_unitset()
        return self._unitset

    def _set_unitset(self, unitset):
        self.set_unitset(unitset=unitset)

    unitset = property(fset=_set_unitset, fget=_get_unitset)

    def _set_storage(self, unit):
        self.storage_unit = self._fix_unit(unit)
        if self.value != 0:
            self.value = self.convert(self.value, self.storage_unit, unit)
        self._is_seed = self._storage_unit == self._seed_unit
        return self

    def _get_storage(self):
        return self._storage_unit

    storage_unit = property(fset=_set_storage, fget=_get_storage)

    # </editor-fold>

    def set(self, value, unit=None, suffix=None):
        """
        Allows setting of the value, unit, and suffix
        """
        if unit is not None:
            self.unit = unit
            self._tmp_unit = unit
        if suffix is not None:
            self.suffix = suffix
        self.value = value

    def get(self, unit=None):
        """
        Allows requesting the value of the object in different units
        :return:
        """
        if unit is None:
            unit = self.unit
        else:
            unit, suffix = self._fix_unit(unit)
        return self._convert(to_unit=unit)

    def get_normalized(self, unitset=None, silent=True, set_unit=False):
        """
        Returns a normalized unit and value, for example:

            >>> ds = DataSizeHelper('1000 Gb')
            >>> ds.get_normalized()
            (1, 'Tb')

        Can also set its own unit to the normalized unit if requested.
        :param unitset: Normalization requires the unitset to be know.  if this cannot be automatically detected, it
        must be passed.
        :param silent: If False, If the unitset is not passed or set, and it cannot be detected, an AttributeError will
        be raised, if True, the normal value and unit will be returned un-normalized.
        :param set_unit: If True, the normalization process will reset the unit to the normalized unit.
        :return:
        """
        unitset = unitset or self.unitset
        if unitset is None:
            if silent:
                return self.value, self.unit
            else:
                raise AttributeError('Normalization requires a unitset to be defined.')

        value, unit = self._calculator(self.value, unit=self.storage_unit, return_as=unitset)
        if set_unit:
            self.unit = unit

        return value, self.unit

    def _unit_info(self, unit=None):
        unit = unit or self.unit
        return self._unit_manager[unit]

    def _fix_unit(self, unit=None):
        tmp_value, tmp_unit, tmp_suffix = self._unit_manager(unit, default_unit=self.unit, default_suffix=self.suffix, unit_only=True)
        return tmp_unit, tmp_suffix

    def _convert(self, value=None, from_unit=None, to_unit=None):
        value = value or self.value
        from_unit = from_unit or self._storage_unit
        to_unit = to_unit or self._storage_unit

        if from_unit == to_unit:
            return value

        tmp_val, tmp_unit = self._calculator(value, from_unit, to_unit)
        return tmp_val

    def _parse_value(self, value, unit=None, suffix=None):
        unit = unit or self.unit
        return self._unit_manager(value, default_unit=unit, default_suffix=suffix)

    def __format__(self, format_spec):

        format_args = {}

        format_keys = format_spec.split(':')

        normalize_keys = dict(
            bb=BIN_BIT,
            by=BIN_BYT,
            db=DEC_BIT,
            dy=DEC_BYT,
            n=self.unitset
        )

        for key in format_keys:

            if key[-1:] == '+':
                format_args['proper_case'] = True
                key = key[:-1]
            if key in ['bb', 'by', 'db', 'dy', 'n']:
                format_args['normalize_to_unitset'] = normalize_keys[key]
            elif key in base_data_units._base_units:
                format_args['force_to_unit'] = key
            elif key in ['S', 's']:
                format_args['include_suffix'] = key == 'S'
            elif key == 'l':
                format_args['pluralize'] = False
            elif key in ['C', 'c']:
                format_args['proper_case'] = key == 'C'
            else:
                if 'number_format' not in format_args:
                    format_args['number_format'] = key

        return self.get_str(**format_args)

    def get_str(self, force_to_unit=None, normalize_to_unitset=None, pluralize=True, proper_case=True,
                long_name=False, include_suffix=True, number_format=None):

        name_format_list = []
        if long_name:
            name_format_list.append('+')
        if proper_case:
            name_format_list.append('C')

        if number_format is None:
            num_key = '{}'
        else:
            num_key = '{:'+number_format+'}'

        if normalize_to_unitset is not None and force_to_unit is not None:
            raise AttributeError('Normalize and force flags cannot be used together')

        if normalize_to_unitset is not None:
            tmp_value, tmp_unit = self.get_normalized(normalize_to_unitset)

        elif force_to_unit is not None:
            tmp_value = self._convert(to_unit=force_to_unit)
            tmp_unit = force_to_unit

        else:
            tmp_value = self._convert(to_unit=self.unit)
            tmp_unit = self.unit

        if tmp_value == 1:
            pluralize = False

        if pluralize:
            name_format_list.append('L')

        tmp_value_str = text_number_formatter(tmp_value, format_spec=number_format)

        tmp_unit_format = '{:'+':'.join(name_format_list)+'}'
        tmp_unit_str = tmp_unit_format.format(self._unit_manager[tmp_unit])

        if include_suffix and self.suffix is not None:
            tmp_suffix_str = self.suffix
        else:
            tmp_suffix_str = ''

        return tmp_value_str+" "+tmp_unit_str+tmp_suffix_str

    def __call__(self, value=None, unit=None):
        if value is None:
            return self.get(unit)
        else:
            self.set(value, unit)
            return self

    def __str__(self):
        return self.get_str()

    def __getattr__(self, item):
        return self.get(unit=item)

    def __setattr__(self, key, value):
        if key in dir(self):
            super().__setattr__(key, value)
        elif key in self._aliases:
            self.set(value, key)
        else:
            raise AttributeError('%s is not a valid method or unit' % key)

    # Comparison Magic Methods

    def _get_storage_value(self, in_obj=None, conv_numeric=True):

        if isinstance(in_obj, self.__class__):
            return in_obj.get(unit=self.storage_unit)
        try:
            tmp_val = Decimal(in_obj)
        except InvalidOperation:
            tmp_val, tmp_unit, tmp_suffix = self._parse_value(value=in_obj)
            return self._convert(tmp_val, from_unit=tmp_unit)
        else:
            if conv_numeric:
                return self._convert(tmp_val, from_unit=self.unit)
            else:
                return tmp_val

    def _comp(self, other):
        return self.value - self._get_storage_value(other)

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
        if operation in ['add', 'sub']:
            other_value = self._get_storage_value(other)
        else:
            other_value = self._get_storage_value(other, conv_numeric=False)

        if operation == 'add':
            new_value = self.get(unit=self.storage_unit) + other_value
        elif operation == 'sub':
            new_value = self.get(unit=self.storage_unit) - other_value

        elif operation == 'mul':
            new_value = self.get(unit=self.storage_unit) * other_value
        elif operation == 'floordiv':
            new_value = self.get(unit=self.storage_unit) // other_value
        elif operation == 'div':
            new_value = self.get(unit=self.storage_unit) / other_value
        elif operation == 'mod':
            new_value = self.get(unit=self.storage_unit) % other_value
        elif operation == 'pow':
            new_value = self.get(unit=self.storage_unit) ** other_value
        elif operation == 'lshift':
            new_value = self.get(unit=self.storage_unit) << other_value
        elif operation == 'rshift':
            new_value = self.get(unit=self.storage_unit) >> other_value
        elif operation == 'and':
            new_value = self.get(unit=self.storage_unit) % other_value
        elif operation == 'or':
            new_value = self.get(unit=self.storage_unit) | other_value
        elif operation == 'xor':
            new_value = self.get(unit=self.storage_unit) ^ other_value
        else:
            raise AttributeError('Invalid operaion: %s' % operation)

        new_value = self._convert(value=new_value, to_unit=self.unit)

        if ret_class and not as_value:
            return self.__class__(
                value=new_value,
                unit=self.unit,
                suffix=self.suffix,
                # default_unit=self._default_unit,
                storage_unit=self.storage_unit,
                unitset=self.unitset,
                unit_manager=self._unit_manager,
                calculator=self._calculator)
        else:
            return new_value

    def __add__(self, other):
        return self._math_helper(other, 'add')

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'add')
        return self
    # --------------------------------------

    def __sub__(self, other):
        return self._math_helper(other, 'sub')

    def __rsub__(self, other):
        return self.__sub__(other)

    def __isub__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'sub')
        return self
    # --------------------------------------

    def __mul__(self, other):
        return self._math_helper(other, 'mul')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'mul')
        return self

    # --------------------------------------

    def __floordiv__(self, other):
        return self._math_helper(other, 'floordiv')

    def __rfloordiv__(self, other):
        return self.__floordiv__(other)

    def __ifloordiv__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'floordiv')
        return self

    # --------------------------------------

    def __div__(self, other):
        return self._math_helper(other, 'div')

    def __rdiv__(self, other):
        return self.__div__(other)

    def __idiv__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'div')
        return self

    # --------------------------------------

    def __mod__(self, other):
        return self._math_helper(other, 'mod')

    def __rmod__(self, other):
        return self.__mod__(other)

    def __imod__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'mod')
        return self

    # --------------------------------------

    def __pow__(self, other):
        return self._math_helper(other, 'pow')

    def __rpow__(self, other):
        return self.__pow__(other)

    def __ipow__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'pow')
        return self

    # --------------------------------------

    def __lshift__(self, other):
        return self._math_helper(other, 'lshift')

    def __rlshift__(self, other):
        return self.__lshift__(other)

    def __ilshift__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'lshift')
        return self

    # --------------------------------------

    def __rshift__(self, other):
        return self._math_helper(other, 'rshift')

    def __rrshift__(self, other):
        return self.__rshift__(other)

    def __irshift__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'rshift')
        return self

    # --------------------------------------

    def __and__(self, other):
        return self._math_helper(other, 'and')

    def __rand__(self, other):
        return self.__and__(other)

    def __iand__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'and')
        return self

    # --------------------------------------

    def __or__(self, other):
        return self._math_helper(other, 'or')

    def __ror__(self, other):
        return self.__or__(other)

    def __ior__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'or')
        return self

    # --------------------------------------

    def __xor__(self, other):
        return self._math_helper(other, 'xor')

    def __rxor__(self, other):
        return self.__xor__(other)

    def __ixor__(self, other):
        self._tmp_unit = self.unit
        self.value = self._math_helper(other, 'xor')
        return self

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
