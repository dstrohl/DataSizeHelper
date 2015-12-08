from data_unit_lookups import *
from decimal import Decimal

__all__ = ['base_data_units', 'DataBaseUnits', 'DataUnit']


def _make_plural(items, reference_key, pluralize):
    if not pluralize:
        return

    tmp_ret = {}
    for item in items:
        tmp_ret[item+'s'] = reference_key

    items.update(tmp_ret)


def _make_caps(items, reference_key, capitalize):
    if not capitalize:
        return

    tmp_ret = {}
    for item in items:
        tmp_ret[item.capitalize()] = reference_key

    items.update(tmp_ret)


def _make_bb_caps(items, reference_key, mangle_case):
    if not mangle_case:
        return

    tmp_ret = {}
    for item in items:
        if BIT in item:
            tmp_ret[item.replace('bit', 'Bit')] = reference_key
        elif BYT in item:
            tmp_ret[item.replace('byte', 'Byte')] = reference_key

    items.update(tmp_ret)

class DataUnit(object):
    def __init__(self, unit_key, unitset):
        self.base_key = unit_key

        self.unitset_info = UNITSET_INFO[unitset]
        self.unit_info = BASEUNITS[unit_key]

        self.short_name = make_unit_name(unit_key, unitset)
        self.long_name = make_unit_name(unit_key, unitset, long=True)

        if unit_key == 'B':
            if BYT in unitset:
                self.unitset = BYT
                self._bitbyte = True
            else:
                self.unitset = BIT
                self._bitbyte = True
        else:
            self.unitset = unitset
            self._bitbyte = False

        self.to_b_multiplier = Decimal(TO_BIT_CONVERSION[self.short_name])

    def convert_unitset(self, unitset):
        return make_unit_name(self.base_key, unitset)

    def full_unitset(self):
        if self._bitbyte:
            return None
        return self.unitset

    def unitset_match(self, unitset):
        if self._bitbyte:
            if unitset in [BIN, DEC]:
                return True
            return self.unitset in unitset
        else:
            return unitset == self.unitset

    def aliases(self, long_name=True, mangle_case=True, plural=True, unitset=None, force_to_unitset=False):
        if force_to_unitset and unitset is None:
            raise AttributeError('Cannot force to unitset if unitset is None')
        if plural and not long_name:
            raise AttributeError('Long names must be enabled to pluralize')

        # if the unitset does not match, but we are trying to force a specific unitset, return nothing
        if unitset is not None and not force_to_unitset:
            if not self.unitset_match(unitset):
                return {}

        # if unitset is used, set the reference key to the correct short name
        if unitset is not None:
            reference_key = make_unit_name(self.base_key, unitset=unitset)
        else:
            reference_key = self.short_name

        tmp_ret = {self.short_name: reference_key}

        # if mangle case is selected, mangle short name cases.
        # handles mb -> Mb, mB -> MB, mib - Mib

        if not self._bitbyte and mangle_case:
            tmp_ret[self.short_name[0].lower()+self.short_name[1:]] = reference_key

        # if mangle case, and forcing to unitset, will handle the specific case of:
        # mb -> MB and mib -> MiB(which is missed above)

        if force_to_unitset and mangle_case and BYT in unitset:
            tmp_ret[self.short_name.lower()] = reference_key

        if long_name:
            tmp_ln_set = {self.long_name: reference_key}

            _make_caps(tmp_ln_set, reference_key, mangle_case)
            _make_plural(tmp_ln_set, reference_key, pluralize=plural)
            _make_bb_caps(tmp_ln_set, reference_key, mangle_case)

            tmp_ret.update(tmp_ln_set)

        return tmp_ret

    def __format__(self, format_spec):
        """
        Custom Format Syntax (separate keys with ':'):

            [+][:s|:S][:l|:L][:c|:C]

            '+':
                Forces the use of long names (such as megabyte instead of Mb).

            The following are only used if long names are used.
            'l' or 'L':
                'l': Do not pluralize.
                'L': pluralize if long names are used [default]

            'c' or 'C':
                'c': Only use lower case
                'C': Use proper case ('Megabyte') [default]

        examples (using 'MB' unit):

            * {} = 'MB'
            * {+} = 'Megabytes'
            * {+l} = 'Megabyte'
            * {+c} = 'megabytes'
            * {+lc} = 'megabyte'

        """
        format_keys = format_spec.split(':')

        long_names = False
        pluralize = False
        proper_case = False

        if 'L' in format_keys:
            if 'l' in format_keys:
                raise AttributeError('Both L and l cannot be used in the format spec')
            pluralize = False

        if 'L' in format_keys:
            if 'l' in format_keys:
                raise AttributeError('Both L and l cannot be used in the format spec')
            pluralize = True

        if '+' in format_keys:
            long_names = True

        if 'c' in format_keys:
            if 'C' in format_keys:
                raise AttributeError('Both C and c cannot be used in the format spec')
            proper_case = False

        if 'C' in format_keys:
            if 'c' in format_keys:
                raise AttributeError('Both C and c cannot be used in the format spec')
            proper_case = True

        if long_names:
            tmp_ret = self.long_name
            if pluralize:
                tmp_ret += 's'
            if proper_case:
                tmp_ret = tmp_ret.capitalize()
        else:
            tmp_ret = self.short_name

        return tmp_ret


class DataBaseUnits(object):

    """
    Helper class that helps provides information about a specific unit.  For example:

    Normally not used directly.

    """


    def __init__(self, limit_to=None):
        """
        :param limit_to: if a unitset string is passed, this will limit the available units to ones that are in that unitset.
        """
        self.limit_to = limit_to

        self._base_units = {}
        self._ref_dict = {}

        self.unitsets = {
            DEC_BIT: [('b', 1)],
            DEC_BYT: [('B', 1)],
            BIN_BIT: [('b', 1)],
            BIN_BYT: [('B', 1)]}

        self._make_initial()

    def _make_initial(self):
        for unit_key in BASEUNITS:
            for unitset in UNITSET_NAMES:
                tmp_unit = DataUnit(unit_key=unit_key, unitset=unitset)

                if self.limit_to is None or tmp_unit.unitset_match(self.limit_to):
                    self._base_units[tmp_unit.short_name] = tmp_unit
                    self._ref_dict[tmp_unit.short_name] = tmp_unit.short_name
                    self.unitsets[unitset].append((tmp_unit.short_name, tmp_unit.to_b_multiplier))

        for item in self.unitsets.values():
            item.sort(key=lambda k: k[1])

    @staticmethod
    def non_specific_aliases(unitset, mangle_case=False):

        tmp_alias_set = dict()
        tmp_alias_set['mg'] = make_unit_name('M', unitset)
        tmp_alias_set['meg'] = make_unit_name('M', unitset)
        tmp_alias_set['gig'] = make_unit_name('G', unitset)

        if mangle_case:
            tmp_alias_set['Mg'] = make_unit_name('M', unitset)
            tmp_alias_set['Meg'] = make_unit_name('M', unitset)
            tmp_alias_set['Gig'] = make_unit_name('G', unitset)

        for key, item in BASEUNITS.items():
            short_name = make_unit_name(key, unitset)
            tmp_alias_set[key] = short_name                       # ex: "M"
            if mangle_case:
                tmp_alias_set[key.lower()] = short_name               # ex: "m"

        return tmp_alias_set

    def keys(self, limit_to=None):
        if limit_to is None:
            return self._ref_dict
        else:
            tmp_ret = {}
            for key, item in self.items(limit_to=limit_to):
                tmp_ret[key] = key

        return tmp_ret

    def items(self, limit_to=None):
        for key, item in self._base_units.items():
            if limit_to is None or item.unitset_match(limit_to):
                yield key, item

    def __iter__(self):
        for key in self._base_units:
            yield key

    def __getitem__(self, item):
        return self._base_units[item]

    def __contains__(self, item):
        return item in self._base_units


base_data_units = DataBaseUnits()
