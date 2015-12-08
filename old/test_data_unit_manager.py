import unittest
# from bytes_helper import DataSizeCalculator, data_size_calculator
from data_unit_lookups import *
from data_unit_calc import *
from decimal import Decimal

class TestDUM(unittest.TestCase):

    def test_normal_1(self):
        test_params = (1, {}, {'value': '2Mb'}, {'value': 2, 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_normal_2(self):
        test_params = (2, {}, {'value': '2-Mb'}, {'value': 2, 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_normal_3(self):
        test_params = (3, {}, {'value': '332-Mb'}, {'value': 332, 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_normal_4(self):
        test_params = (4, {}, {'value': '.2-Mb'}, {'value': Decimal('0.2'), 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_normal_5(self):
        test_params = (5, {}, {'value': '0.2-Mb'}, {'value': Decimal('0.2'), 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_normal_6(self):
        test_params = (6, {}, {'value': '-2-Mb'}, {'value': -2, 'unit': 'Mb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_long_names_1(self):

        # include long names
        test_params = (9, {}, {'value': '0.2-Kilobits'}, {'value': Decimal('0.2'), 'unit': 'Kb'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_long_names_2(self):
        test_params = (10, {}, {'value': '39 KiloBytes'}, {'value': 39, 'unit': 'KB'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_basic_suffixes_1(self):
        dum = DataUnitManager(suffix_sets=SUFFIX_SETS)
        # include basic suffix
        test_params = (11, {}, {'value': '0.2-Megabits/sec'}, {'value': Decimal('0.2'), 'unit': 'Mb', 'suffix': '/s'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_basic_suffixes_2(self):
        dum = DataUnitManager(suffix_sets=SUFFIX_SETS)

        test_params = (12, {}, {'value': '0.2-Megabits/s'}, {'value': Decimal('0.2'), 'unit': 'Mb', 'suffix': '/s'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_1a(self):
        dum = DataUnitManager(unitset=DEC_BYT, allow_incorrect_case=True, force_non_specific=True, force_to_unitset=True)
        # include case problems with unitset
        test_params = (16, {}, {'value': '2mb'}, {'value': 2, 'unit': 'MB'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_2(self):
        dum = DataUnitManager(unitset=DEC_BIT, force_non_specific=True)
        test_params = (17, {}, {'value': '2m'}, {'value': 2, 'unit': 'Mb'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_3(self):
        dum = DataUnitManager(unitset=DEC_BYT, force_to_unitset=True)
        test_params = (18, {}, {'value': '332-b'}, {'value': 332, 'unit': 'B'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_4(self):
        dum = DataUnitManager(unitset=BIN_BYT, force_to_unitset=True)
        test_params = (19, {}, {'value': '.2-Mb'}, {'value': Decimal('0.2'), 'unit': 'MiB'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_5(self):
        dum = DataUnitManager(unitset=BIN_BIT, force_to_unitset=True)
        test_params = (20, {}, {'value': '0.2-Mb'}, {'value': Decimal('0.2'), 'unit': 'Mib'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_6(self):
        dum = DataUnitManager(unitset=BIN_BYT, force_non_specific=True)
        test_params = (21, {}, {'value': '.2-meg'}, {'value': Decimal('0.2'), 'unit': 'MiB'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_case_problems_with_unitset_7(self):
        dum = DataUnitManager(unitset=BIN_BIT, force_non_specific=True)
        test_params = (22, {}, {'value': '0.2-gig'}, {'value': Decimal('0.2'), 'unit': 'Gib'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_number_passing_1(self):

        # passing numbers
        test_params = (29, {}, {'value': 2}, {'value': 2, 'unit': 'B'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_number_passing_2(self):
        test_params = (30, {}, {'value': '2'}, {'value': 2, 'unit': 'B'})
        test_resp = data_units(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

    def test_number_passing_3(self):
        dum = DataUnitManager(default_unit='Mb')
        test_params = (31, {}, {'value': 200}, {'value': 200, 'unit': 'Mb'})
        test_resp = dum(**test_params[2])

        for dso_attrib, tmp_check in test_params[3].items():
            tmp_validation = test_resp[dso_attrib]
            with self.subTest(m=dso_attrib):
                self.assertEqual(tmp_check, tmp_validation)

