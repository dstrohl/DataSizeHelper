from copy import copy
import math
from data_unit_lookups import *
from data_base_units import *
from starts_ends_with import StartsEndsWith
from decimal import Decimal, InvalidOperation

__all__ = ['DataUnitManager', 'data_units', 'data_size_calculator', 'DataSizeCalculator']

class DataUnitManager(object):
    DECIMAL_BYTE = 'decimal-byte'
    DECIMAL_BIT = 'decimal-bit'
    BINARY_BYTE = 'binary-byte'
    BINARY_BIT = 'binary-bit'
    BIT = 'bit'
    BYTE = 'byte'
    BINARY = 'binary'
    DECIMAL = 'decimal'

    _suffix_check_helper = None

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

    a default instance is created as 'data_units', however if you wish to limit or tune how the class handles units, you
    can instantiate your own.

    This creates the list of aliases on instantiation, so if you want different options, you must create different
    objects.

    examples:

        >>> from data_units import data_units

        >>> data_units('megabytes', units_only=True)
        ('Mb', '')

        >>> data_units('1 gig/sec')
        (Decimal('1'), 'Gb', '/s')
    """


    def __init__(self,
                 unitset=None,
                 allow_long_names=True,
                 allow_plural_names=True,
                 allow_incorrect_case=True,
                 force_non_specific=False,
                 force_to_unitset=False,
                 suffix_sets=None,
                 parse_method='strict',   # ['strict'|'loose_unit'|'loose_suffix'|'loose']
                 default_unit='B',
                 allow_caching=True,
                 ):
        """

        :param str unitset: What unitset to use.  This is required if force to unitset is set, as well as some of the alias
        options
        :param bool allow_long_names: [default=True] if True, detect long names (such as 'megabyte')
        :param bool allow_plural_names: [default=True] if True, detect plural long names (such as 'megabytes')
        :param bool allow_incorrect_case: [default=True] if True, detect incorrect case (such as 'MegaByte' or 'megaByte')
        :param bool force_non_specific: [default=False] REQUIRES unitset to be set.  will force non-specific units to
            the specified unitset, for example, 'gig' to 'Gb', or 'm' to 'MB'.
        :param bool force_to_unitset: [default=False] REQUIRES unitset to be set.  Will force similar units in different
            unitsets to the specified unitset.  For example, 'Gb' to 'Gib'
        :param dict suffix_sets: [default=None] Defines allowed suffix's and normalizes them (for example '/sec' to
            '/s'). This would be passed as a dictionary in the format of:
            {'<official suffix>': ['<alias>','<alias>',...]}
        :param str parse_method: ['strict'|'loose_unit'|'loose_suffix'] default='strict'
            'strict':
                Will only parse if any text found matches a unit and optionally a suffix.
            'loose-suffix':
                Will parse for a unit match with the list of alias's, but if the suffix does not match anything in the
                suffix list, it will return the suffix found.
            'loose-unit':
                Will parse for a suffix that must match, but will return the passed unit if it does not match.  (not
                recommended for normal use since this may cause key errors in other modules.)
        :param str default_unit: [default='B'], if no unit is passed, the system assumes this unit.
        :param bool allow_caching: [default=True], for troubleshooting, turns off caching of results.
        """

        if (force_non_specific or force_to_unitset) and unitset is None:
            raise AttributeError('Unitset must be set to force convert units')

        self._unitset = unitset
        self._allow_long_names = allow_long_names
        self._allow_plural_names = allow_plural_names
        self._allow_incorrect_case = allow_incorrect_case
        self._force_non_specific = force_non_specific
        self._force_to_unitset = force_to_unitset
        self._suffixes = {}

        self._unit_lookup_cache = {}
        self._allow_caching = allow_caching

        self.default_unit = default_unit
        if parse_method not in ['strict', 'loose_unit', 'loose_suffix', 'loose']:
            raise AttributeError("parse method must be one of: ['strict'|'loose_unit'|'loose_suffix']")
        self.parse_method = parse_method
        self._unit_dict = {}

        self.suffixes = suffix_sets  # this also runs the make_unit_list method


    # <editor-fold desc=" ********************* Properties ****************************************">
    def get_unitset(self):
        return self._unitset

    def set_unitset(self, value):
        self._unitset = value
        self._make_alias_list()

    unitset = property(fget=get_unitset, fset=set_unitset)

    def get_allow_long_names(self):
        return self._allow_long_names

    def set_allow_long_names(self, value):
        self._allow_long_names = value
        self._make_alias_list()

    allow_long_names = property(fget=get_allow_long_names, fset=set_allow_long_names)

    def get_allow_plural_names(self):
        return self._allow_plural_names

    def set_allow_plural_names(self, value):
        self._allow_plural_names = value
        self._make_alias_list()

    allow_plural_names = property(fget=get_allow_plural_names, fset=set_allow_plural_names)

    def get_allow_incorrect_case(self):
        return self._allow_incorrect_case

    def set_allow_incorrect_case(self, value):
        self._allow_incorrect_case = value
        self._make_alias_list()

    allow_incorrect_case = property(fget=get_allow_incorrect_case, fset=set_allow_incorrect_case)

    def get_force_non_specific(self):
        return self._force_non_specific

    def set_force_non_specific(self, value):
        self._force_non_specific = value
        self._make_alias_list()

    force_non_specific = property(fget=get_force_non_specific, fset=set_force_non_specific)

    def get_force_to_unitset(self):
        return self._force_to_unitset

    def set_force_to_unitset(self, value):
        self._force_to_unitset = value
        self._make_alias_list()

    force_to_unitset = property(fget=get_force_to_unitset, fset=set_force_to_unitset)

    def get_suffix_set(self):
        return self._suffixes

    def set_suffix_set(self, value):
        self._suffixes = {}
        if value is not None:
            if isinstance(value, dict):
                for alias, suffix_list in value.items():
                    if isinstance(suffix_list, str):
                        suffix_list = [suffix_list]
                    for suffix in suffix_list:
                        self._suffixes[suffix] = alias
            elif isinstance(value, str):
                self._suffixes[value] = value
            elif isinstance(value, (list, tuple)):
                for suffix in value:
                    self.set_suffix_set(suffix)
        self._make_alias_list()

    suffixes = property(fget=get_suffix_set, fset=set_suffix_set)
    # </editor-fold>

    def _make_alias_list(self):

        self._unit_dict = {}
        if self.force_to_unitset:
            limit_to = None
        else:
            limit_to = self.unitset
        for unit, unit_info in base_data_units.items(limit_to=limit_to):
            tmp_unit_dict = unit_info.aliases(
                long_name=self.allow_long_names,
                mangle_case=self.allow_incorrect_case,
                plural=self.allow_plural_names,
                unitset=self.unitset,
                force_to_unitset=self.force_to_unitset)

            self._unit_dict.update(tmp_unit_dict)

        if self.unitset and self.force_non_specific:
            tmp_unit_dict = base_data_units.non_specific_aliases(unitset=self.unitset, mangle_case=self.allow_incorrect_case)
            self._unit_dict.update(tmp_unit_dict)

        self._suffix_check_helper = StartsEndsWith(
            prefixes=list(self._unit_dict),
            suffixes=list(self._suffixes),
            case_insensitive=self.allow_incorrect_case,
        )

    def _parse_item(self, value, default_unit=None, default_suffix=None):
        tmp_value, tmp_unit = self._parse_value(value)
        tmp_unit, tmp_suffix = self._parse_unit(tmp_unit, default_unit=default_unit, default_suffix=default_suffix)

        '''
        tmp_ret = dict(
            value=tmp_value,
            unit=tmp_unit,
            suffix=tmp_suffix,
        )
        '''
        return tmp_value, tmp_unit, tmp_suffix

    def _parse_unit(self, unit=None, default_unit=None, default_suffix=None):

        if unit is None:
            return default_unit or self.default_unit, default_suffix

        if unit in self._unit_dict:
            return self._unit_dict[unit], default_suffix

        if self._allow_caching:
            lookup_unit_name = '%s-%s-%s' % (unit, default_unit, default_suffix)
            try:
                return self._unit_lookup_cache[lookup_unit_name]
            except KeyError:
                pass

        default_unit = default_unit or self.default_unit
        tmp_unit = None
        tmp_suffix = None

        # must only consist of a unit and optional suffix, both of which must match one on the list.
        if self.parse_method == 'strict':
            tmp_unit, remainder, tmp_suffix = self._suffix_check_helper(unit)

            if remainder:
                tmp_msg = 'Unit and suffix could not be determined, one or the other did not match.'
                tmp_msg += '\nWe found "%s" / "%s" / "%s"' % (tmp_unit, remainder, tmp_suffix)
                raise AttributeError(tmp_msg)

            tmp_unit = self._unit_dict.get(tmp_unit, default_unit)
            tmp_suffix = self._suffixes.get(tmp_suffix, default_suffix)

        # will match the unit if found, and the suffix if found, or will return the
        # rest as a suffix, even if unmatched
        elif self.parse_method == 'loose_suffix':
            tmp_unit, remainder, tmp_suffix = self._suffix_check_helper(unit, prefix_priority=True)

            if tmp_suffix is None:
                if remainder is not None:
                    tmp_suffix = remainder
                else:
                    tmp_suffix = None

            tmp_unit = self._unit_dict.get(tmp_unit, default_unit)
            if tmp_suffix == '' or tmp_suffix is None:
                tmp_suffix = default_suffix
            else:
                tmp_suffix = self._suffixes.get(tmp_suffix, tmp_suffix)

        # will match the suffix if found, and the unit if found, and return the rest as a unit if unfound,
        # normally should not be used unless only parsing is desired (may break other methods)
        elif self.parse_method == 'loose_unit':
            tmp_unit, remainder, tmp_suffix = self._suffix_check_helper(unit, prefix_priority=False)

            if tmp_unit is None:
                if remainder is not None:
                    tmp_unit = remainder
                else:
                    tmp_unit = ''

            if tmp_unit is None or tmp_unit == '':
                tmp_unit = default_unit
            else:
                tmp_unit = self._unit_dict.get(tmp_unit, tmp_unit)
            tmp_suffix = self._suffixes.get(tmp_suffix,default_suffix)

        if tmp_unit == '' or tmp_unit is None:
            raise AttributeError('Could not parse unit out of %s' % unit)

        if self._allow_caching:
            self._unit_lookup_cache[lookup_unit_name] = tmp_unit, tmp_suffix

        return tmp_unit, tmp_suffix

    def _parse_value(self, value):

        tmp_value = value
        tmp_unit = ''

        if isinstance(value, (int, float, Decimal)):
            return tmp_value, tmp_unit

        try:
            tmp_value = Decimal(value)
            return tmp_value, tmp_unit
        except InvalidOperation:
            pass

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
                tmp_value = Decimal(tmp_value)
                return tmp_value, tmp_unit
            except InvalidOperation:
                raise AttributeError('%s could not be converted to a numeric value (from %s)' % (tmp_value, value))

        raise TypeError('%s was not a string or numeric' % value)

    def items(self):
        """
        Returns the dictionary of aliases -> short names.
        """
        return self._unit_dict

    def aliases(self):
        """
        Returns a list of aliases
        """
        return list(self._unit_dict)

    def base_units(self):
        """
        Returns a list of the base names recognized
        :return:
        """
        return list(base_data_units._base_units)

    def __len__(self):
        return len(self._unit_dict)

    def __getitem__(self, item):
        return base_data_units[item]

    def __contains__(self, item):
        return item in self._unit_dict

    def __call__(self, value, unit_only=False, default_unit=None, default_suffix=None):
        """
        The primary interface with this class is by calling the instantiated object.  This takes a value and parses
        it into its separate pieces.

        :param value: The item to parse
        :param bool unit_only: [default=False] if True, will not attempt to parse a number from the value.  used to
        clean up and verify unit strings only.  If False (the default), the system will attempt to parse out an initial
        number from the passed value.

        This also modifies how the data is returned, if True, the data is returned in a tuple with two objects;
        (unit, suffix), if False, the data is returned in a three object tuple; (value, unit, suffix)

        :param str default_unit: The unit to use if none was found. (overrides the default unit passed during init.)
        :param str default_suffix: The suffix to use if none was found
        :return:
        """

        if unit_only:
            tmp_unit, tmp_suffix = self._parse_unit(unit=value, default_unit=default_unit, default_suffix=default_suffix)
            # tmp_ret['unit'] = tmp_unit
            # tmp_ret['suffix'] = tmp_suffix
            return None, tmp_unit, tmp_suffix
        else:
            return self._parse_item(value=value, default_unit=default_unit, default_suffix=default_suffix)

data_units = DataUnitManager(
    allow_long_names=True,
    default_unit='B')


class DataSizeCalculator(object):
    DEC_BYT = DEC_BYT
    DEC_BIT = DEC_BIT
    BIN_BIT = BIN_BIT
    BIN_BYT = BIN_BYT

    def __init__(self):
        self._base_units = {}

        self._unitsets = {
            DEC_BIT: [('b', 1)],
            DEC_BYT: [('B', 1)],
            BIN_BIT: [('b', 1)],
            BIN_BYT: [('B', 1)]}

        self._make_initial()

    def _make_initial(self):

        for unit, unit_info in base_data_units.items():
            self._base_units[unit_info.short_name] = {}

            if unit_info.base_key != 'B':
                self._unitsets[unit_info.unitset].append((unit_info.short_name, unit_info.to_b_multiplier))

            self._base_units[unit_info.short_name] = {'to': {}}
            self._base_units[unit_info.short_name]['to']['b'] = unit_info.to_b_multiplier

        for item in self._unitsets.values():
            item.sort(key=lambda k: k[1])

    def _get_mult(self, from_unit, to_unit):
        tmp_from = self._base_units[from_unit]['to']
        try:
            return tmp_from[to_unit]
        except KeyError:
            tmp_from_bits = self._get_mult(from_unit, 'b')
            tmp_to_bits = self._get_mult(to_unit, 'b')
            tmp_from[to_unit] = tmp_from_bits / tmp_to_bits
            return tmp_from[to_unit]

    def convert(self, value, from_unit, to_unit='b'):
        value = Decimal(value)
        tmp_value = value * self._get_mult(from_unit, to_unit)
        return tmp_value

    def normalize(self, value, unit, unitset):
        value = Decimal(value)

        base_value = self.convert(value, from_unit=unit)
        norm_unit = 'b'
        for item in self._unitsets[unitset]:
            if base_value < item[1]:
                break
            norm_unit = item[0]

        value = self.convert(base_value, from_unit='b', to_unit=norm_unit)
        unit = norm_unit

        return value, unit

    def __call__(self, value, unit, return_as):
        """
        Converts between units and normalizes within a unitset.

        :param value: A numeric value (can be a string, int, float, or decimal, as long as it can be converted to a
            Decimal)
        :param str unit: A string indicating what type if unit this is currently.  The unit must be a standard
            short-name or an AttributeError will be raised.
        :param str return_as: A string indicating what to convert the unit to, if a unit string ('Mb', 'MB', Kib',
            etc...) is passed, this will convert the value to that unit.  if a unitset string is passed, this will
            normalize within that unit.
        :return: This returns a tuple in the format of:
            (Decimal('value'), 'unit short name')
        """
        value = Decimal(value)

        if return_as in UNITSET_NAMES:
            value, unit = self.normalize(value, unit=unit, unitset=return_as)

        else:
            value = self.convert(value, from_unit=unit, to_unit=return_as)
            unit = return_as

        return value, unit

data_size_calculator = DataSizeCalculator()
