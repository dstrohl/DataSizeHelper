import unittest
from data_base_units import *
from data_unit_lookups import *


class TestDataUnitObj(unittest.TestCase):
    maxDiff = None

    def test_base_load_DEC_BYT(self):
        du = DataUnit('M', DEC_BYT)

        self.assertEqual('MB', du.short_name)
        self.assertEqual('megabyte', du.long_name)
        self.assertEqual(8000000, du.to_b_multiplier)

    def test_unitset_match(self):
        du = DataUnit('M', DEC_BYT)

        self.assertTrue(du.unitset_match(DEC_BYT))
        self.assertFalse(du.unitset_match(DEC_BIT))
        self.assertFalse(du.unitset_match(BIN_BYT))
        self.assertFalse(du.unitset_match(BIN_BIT))


    def test_unitset_match_B(self):
        du = DataUnit('B', DEC_BYT)

        self.assertTrue(du.unitset_match(DEC_BYT))
        self.assertFalse(du.unitset_match(DEC_BIT))
        self.assertTrue(du.unitset_match(BIN_BYT))
        self.assertFalse(du.unitset_match(BIN_BIT))

        self.assertTrue(du.unitset_match(BIN))
        self.assertTrue(du.unitset_match(DEC))

        self.assertTrue(du.unitset_match(BYT))
        self.assertFalse(du.unitset_match(BIT))


    def test_unitset_match_b(self):
        du = DataUnit('B', BIN_BIT)

        self.assertFalse(du.unitset_match(DEC_BYT))
        self.assertTrue(du.unitset_match(DEC_BIT))
        self.assertFalse(du.unitset_match(BIN_BYT))
        self.assertTrue(du.unitset_match(BIN_BIT))

        self.assertTrue(du.unitset_match(BIN))
        self.assertTrue(du.unitset_match(DEC))

        self.assertFalse(du.unitset_match(BYT))
        self.assertTrue(du.unitset_match(BIT))


    def test_base_load_DEC_BIT(self):
        du = DataUnit('M', DEC_BIT)

        self.assertEqual('Mb', du.short_name)
        self.assertEqual('megabit', du.long_name)
        self.assertEqual(1000000, du.to_b_multiplier)

    def test_base_load_BIN_BYT(self):
        du = DataUnit('M', BIN_BYT)

        self.assertEqual('MiB', du.short_name)
        self.assertEqual('mebibyte', du.long_name)
        self.assertEqual(8388608, du.to_b_multiplier)

    def test_base_load_BIN_BIT(self):
        du = DataUnit('M', BIN_BIT)

        self.assertEqual('Mib', du.short_name)
        self.assertEqual('mebibit', du.long_name)
        self.assertEqual(1048576, du.to_b_multiplier)


    def test_aliases_DEC_BYT(self):
        du = DataUnit('M', DEC_BYT)
        expected_aliases = {'MB': 'MB'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=False,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'MB': 'MB', 'megabyte': 'MB'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'MB': 'MB', 'megabyte': 'MB', 'megabytes': 'MB'}
        tmp_aliases = du.aliases(unitset=DEC_BYT, long_name=True,
                                 plural=True, mangle_case=False, force_to_unitset=False)


        self.assertDictEqual(expected_aliases, tmp_aliases)
        expected_aliases = {'MB': 'MB', 'megabyte': 'MB', 'Megabyte': 'MB', 'MegaByte': 'MB',
                            'megabytes': 'MB', 'Megabytes': 'MB', 'MegaBytes': 'MB', 'mB': 'MB',
                            'megaByte': 'MB', 'megaBytes': 'MB'}

        tmp_aliases = du.aliases(unitset=DEC_BYT, long_name=True,
                                 plural=True, mangle_case=True, force_to_unitset=False)

        print('response: ', tmp_aliases)
        self.assertDictEqual(expected_aliases, tmp_aliases)

        expected_aliases = {'MB': 'MB', 'megabyte': 'MB', 'Megabyte': 'MB', 'MegaByte': 'MB',
                            'megabytes': 'MB', 'Megabytes': 'MB', 'MegaBytes': 'MB', 'mB': 'MB',
                            'megaByte': 'MB', 'megaBytes': 'MB', 'mb': 'MB'}

        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'MB': 'Mb', 'megabyte': 'Mb', 'Megabyte': 'Mb', 'MegaByte': 'Mb',
                            'megabytes': 'Mb', 'Megabytes': 'Mb', 'MegaBytes': 'Mb', 'mB': 'Mb',
                            'megaByte': 'Mb', 'megaBytes': 'Mb'}

        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'MB': 'Mib', 'megabyte': 'Mib', 'Megabyte': 'Mib', 'MegaByte': 'Mib',
                            'megabytes': 'Mib', 'Megabytes': 'Mib', 'MegaBytes': 'Mib', 'mB': 'Mib',
                            'megaByte': 'Mib', 'megaBytes': 'Mib'}

        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))


    def test_aliases_b_DEC_BIT(self):
        du = DataUnit('B', DEC_BIT)
        expected_aliases = {}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'b': 'b', 'bit': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BYT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'b': 'b', 'bit': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BIT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'b': 'b', 'bit': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'b': 'b', 'bit': 'b', 'bits': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=True, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'b': 'b', 'bit': 'b', 'Bit': 'b', 'bits': 'b', 'Bits': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=False))

        expected_aliases = {'b': 'B', 'bit': 'B', 'Bit': 'B', 'bits': 'B', 'Bits': 'B'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BYT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'b': 'b', 'bit': 'b', 'Bit': 'b', 'bits': 'b', 'Bits': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'b': 'b', 'bit': 'b', 'Bit': 'b', 'bits': 'b', 'Bits': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))


    def test_B_load_DEC_BYT(self):
        du = DataUnit('B', DEC_BYT)

        self.assertEqual('B', du.short_name)
        self.assertEqual('byte', du.long_name)
        self.assertEqual(8, du.to_b_multiplier)

    def test_B_load_DEC_BIT(self):
        du = DataUnit('B', DEC_BIT)

        self.assertEqual('b', du.short_name)
        self.assertEqual('bit', du.long_name)
        self.assertEqual(1, du.to_b_multiplier)

    def test_B_load_BIN_BYT(self):
        du = DataUnit('B', BIN_BYT)

        self.assertEqual('B', du.short_name)
        self.assertEqual('byte', du.long_name)
        self.assertEqual(8, du.to_b_multiplier)

    def test_B_load_BIN_BIT(self):
        du = DataUnit('B', BIN_BIT)

        self.assertEqual('b', du.short_name)
        self.assertEqual('bit', du.long_name)
        self.assertEqual(1, du.to_b_multiplier)


    def test_aliases_B_DEC_BYT(self):
        du = DataUnit('B', DEC_BYT)
        expected_aliases = {}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'B': 'B', 'byte': 'B'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=False, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'B': 'B', 'byte': 'B', 'bytes': 'B'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=True, mangle_case=False, force_to_unitset=False))

        expected_aliases = {'B': 'B', 'byte': 'B', 'Byte': 'B', 'bytes': 'B', 'Bytes': 'B'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BYT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=False))

        expected_aliases = {'B': 'B', 'byte': 'B', 'Byte': 'B', 'bytes': 'B', 'Bytes': 'B', 'b': 'B'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BYT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'B': 'b', 'byte': 'b', 'Byte': 'b', 'bytes': 'b', 'Bytes': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=DEC_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))

        expected_aliases = {'B': 'b', 'byte': 'b', 'Byte': 'b', 'bytes': 'b', 'Bytes': 'b'}
        self.assertDictEqual(expected_aliases, du.aliases(unitset=BIN_BIT, long_name=True,
                                                          plural=True, mangle_case=True, force_to_unitset=True))


    def test_convert_unitset(self):
        du = DataUnit('M', DEC_BYT)
        self.assertEqual('Mib', du.convert_unitset(BIN_BIT))

        du = DataUnit('B', DEC_BYT)
        self.assertEqual('b', du.convert_unitset(BIN_BIT))

    def test_full_unitset(self):
        du = DataUnit('M', DEC_BYT)
        self.assertEqual(DEC_BYT, du.full_unitset())

        du = DataUnit('B', DEC_BYT)
        self.assertEqual(None, du.full_unitset())


    def test_format(self):
        du = DataUnit('M', DEC_BYT)

        self.assertEqual('MB', '{}'.format(du))
        self.assertEqual('megabyte', '{:+}'.format(du))
        self.assertEqual('Megabyte', '{:C:+}'.format(du))
        self.assertEqual('Megabytes', '{:C:+:L}'.format(du))
        self.assertEqual('MB', '{:C}'.format(du))
        self.assertEqual('MB', '{:L}'.format(du))


class TestDataUnitManager(unittest.TestCase):
    maxDiff = None

    def test_base_lookup(self):
        dum = DataBaseUnits()

        self.assertEqual('Kb', dum['Kb'].short_name)
        self.assertEqual('megabit', dum['Mb'].long_name)
        self.assertEqual(1152921504606850000, dum['Eib'].to_b_multiplier)

    def test_limit_to(self):

        dum = DataBaseUnits(limit_to=DEC_BYT)

        self.assertEqual('KB', dum['KB'].short_name)

        with self.assertRaises(KeyError):
            junk = dum['Kb']

        with self.assertRaises(KeyError):
            junk = dum['Kib']

        with self.assertRaises(KeyError):
            junk = dum['KiB']


    def test_non_specific_aliases(self):
        dum = DataBaseUnits()

        expected_resp = {'mg': 'MB', 'meg': 'MB', 'gig': 'GB', 'B': 'B',
                         'M': 'MB', 'K': 'KB', 'G': 'GB', 'T': 'TB', 'P': 'PB', 'E': 'EB', 'Z': 'ZB', 'Y': 'YB'}

        self.assertDictEqual(expected_resp, dum.non_specific_aliases(DEC_BYT, mangle_case=False))

        expected_resp = {'mg': 'Mb', 'meg': 'Mb', 'gig': 'Gb', 'B': 'b',
                         'M': 'Mb', 'K': 'Kb', 'G': 'Gb', 'T': 'Tb', 'P': 'Pb', 'E': 'Eb', 'Z': 'Zb', 'Y': 'Yb'}

        self.assertDictEqual(expected_resp, dum.non_specific_aliases(DEC_BIT, mangle_case=False))

        expected_resp = {'mg': 'MiB', 'meg': 'MiB', 'gig': 'GiB', 'B': 'B',
                         'M': 'MiB', 'K': 'KiB', 'G': 'GiB', 'T': 'TiB', 'P': 'PiB', 'E': 'EiB', 'Z': 'ZiB', 'Y': 'YiB'}

        self.assertDictEqual(expected_resp, dum.non_specific_aliases(BIN_BYT, mangle_case=False))

        expected_resp = {'mg': 'Mib', 'meg': 'Mib', 'gig': 'Gib', 'B': 'b',
                         'M': 'Mib', 'K': 'Kib', 'G': 'Gib', 'T': 'Tib', 'P': 'Pib', 'E': 'Eib', 'Z': 'Zib', 'Y': 'Yib'}

        self.assertDictEqual(expected_resp, dum.non_specific_aliases(BIN_BIT, mangle_case=False))



    def test_keys(self):
        pass

    def test_items(self):
        pass

    def test_iter(self):
        pass

    def test_contains(self):
        dum = DataBaseUnits(limit_to=DEC_BYT)

        self.assertIn('KB', dum)
        self.assertNotIn('Kb', dum)
        self.assertNotIn('foo', dum)


'''
class TestDSC2(unittest.TestCase):

    def _run_dsc(self, dsc_params=None, call_params=None, dso_attrib=None, attrib_value=None, dsc=None):
        if dsc_params is not None and dsc_params != {}:
            dsc = DataSizeCalculator(**dsc_params)
        else:
            dsc = data_size_calculator

        base_msg = 'DSC%r%r.%s' % (dsc_params, call_params, dso_attrib)
        base_msg = base_msg.replace('{', '(').replace('}', ')')

        print('Trying: ', base_msg)

        try:
            tmp_check = dsc(**call_params)
        except Exception as err:
            msg = '%s FAILED' % (base_msg)

            print('  FAILED: ', msg, '\n\n')

            return None, None, msg, err
        else:
            tmp_validation = getattr(tmp_check, dso_attrib)

            msg = '%s = %s, --  expected: %s  --  (dso:%s)' % (base_msg, tmp_validation, attrib_value, tmp_check)

            print('  Finished: ', msg, '\n\n')

            return attrib_value, tmp_validation, msg, None

    def _raise_dsc_test(self, test):
        tmp_params = {}
        if len(test) == 1:
            call_params = test[0]
            dsc_params = {}
        elif len(test) > 1:
            dsc_params = test[0]
            call_params = test[1]

        if len(test) == 3:
            test_exception = test[2]
        else:
            test_exception = AttributeError

        if dsc_params is not None and dsc_params != {}:
            dsc = DataSizeCalculator(**dsc_params)
        else:
            dsc = data_size_calculator

        base_msg = 'DSC%r%r' % (dsc_params, call_params)
        base_msg = base_msg.replace('{', '(').replace('}', ')')
        base_msg += ' Should have raised an exception'

        return dsc, call_params, base_msg, test_exception

    def test_parse(self):
        test_set = [
            # normal


            (1, {}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb'}),
            (2, {}, {'value': '2-Mb'}, {'value': 2, 'unit': 'Mb'}),
            (3, {}, {'value': '332-Mb'}, {'value': 332, 'unit': 'Mb'}),
            (4, {}, {'value': '.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
            (5, {}, {'value': '0.2-Mb'}, {'value': 0.2, 'unit': 'Mb'}),
            (6, {}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb'}),


            # override units
            (7, {}, {'value': '0.2-Mb', 'unit': 'Kb'}, {'value': 0.2, 'unit': 'Kb'}),
            (8, {}, {'value': '-2-Mb', 'unit': 'MiB'}, {'value': -2, 'unit': 'MiB'}),

            # include long names
            (9, {}, {'value': '0.2-Kilobits'}, {'value': 0.2, 'unit': 'Kb'}),
            (10, {}, {'value': '39 KiloBytes'}, {'value': 39, 'unit': 'KB'}),

            # include basic suffix
            (11, {}, {'value': '0.2-Megabits/sec'}, {'value': 0.2, 'unit': 'Mb', 'suffix': '/s'}),
            (12, {}, {'value': '0.2-Megabits/s'}, {'value': 0.2, 'unit': 'Mb', 'suffix': '/s'}),

            # override suffix
            (13, {}, {'value': '0.2-Mb', 'unit': 'Kb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Kb', 'suffix': '/s'}),
            (14, {}, {'value': '0.2-Gb', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),
            # will fail: (15, {}, {'value': '0.2-Gb/min', 'suffix': '/s'}, {'value': 0.2, 'unit': 'Gb', 'suffix': '/s'}),


            # include case problems with unitset
            (16, {}, {'value': '2mb', 'unitset': DEC_BYT}, {'value': 2, 'unit': 'MB'}),
            (17, {}, {'value': '2m', 'unitset': DEC_BIT}, {'value': 2, 'unit': 'Mb'}),
            (18, {}, {'value': '332-b', 'unitset': DEC_BYT}, {'value': 332, 'unit': 'B'}),
            (19, {}, {'value': '.2-Mb', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MiB'}),
            (20, {}, {'value': '0.2-Mb', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Mib'}),
            (21, {}, {'value': '.2-meg', 'unitset': BIN_BYT}, {'value': 0.2, 'unit': 'MB'}),
            (22, {}, {'value': '0.2-gig', 'unitset': BIN_BIT}, {'value': 0.2, 'unit': 'Gib'}),

            # detect unitset
            (23, {}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb', 'unitset': None}),
            (24, {}, {'value': '2-MB'}, {'value': 2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            (25, {}, {'value': '332-Mib'}, {'value': 332, 'unit': 'Mb', 'unitset': BIN_BIT}),
            (26, {}, {'value': '.2-b'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BIT}),
            (27, {}, {'value': '0.2-KB'}, {'value': 0.2, 'unit': 'Mb', 'unitset': DEC_BYT}),
            (28, {}, {'value': '-2-KiB'}, {'value': -2, 'unit': 'Mb', 'unitset': BIN_BYT}),

            # passing numbers
            (29, {}, {'value': 2}, {'value': 2, 'unit': 'B'}),
            (30, {}, {'value': '2'}, {'value': 2, 'unit': 'B'}),
            (31, {}, {'value': 200, 'unit': 'Mb'}, {'value': 200, 'unit': 'Mb'}),


        ]

        test_raises = [
            ({'value': 'blah'},),
            ({'value': '0.2-Gb/min', 'suffix': '/s'},),
        ]

        for test in test_set:
            print('**** TEST: ', test[0], '*******')
            for dso_attrib, attrib_value in test[3].items():
                expected, returned, msg, pass_fail = self._run_dsc(dsc_params=test[1], call_params=test[2],
                                                        dso_attrib=dso_attrib, attrib_value=attrib_value)
                with self.subTest(N=test[0], m=msg):
                    if pass_fail is not None:
                        raise pass_fail
                    self.assertEqual(expected, returned)

        for test in test_raises:
            dsc, dsc_params, msg, test_exception = self._raise_dsc_test(test)
            with self.subTest(m=msg):
                with self.assertRaises(test_exception):
                    tmp_check = dsc(**dsc_params)

'''
