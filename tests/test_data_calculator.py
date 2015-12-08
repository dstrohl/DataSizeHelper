import unittest
from data_unit_calc import DataSizeCalculator, data_size_calculator
from data_unit_lookups import *
from decimal import Decimal

class TestDataCalc(unittest.TestCase):

   def test_call(self):
        test_sets = [
            ({'value': 1000, 'unit': 'B', 'return_as': DEC_BIT}, 8, 'Kb'),
            ({'value': '.0001', 'unit': 'Kb', 'return_as': DEC_BIT}, Decimal('0.1'), 'b'),
            ({'value': 2000, 'unit': 'Kb', 'return_as': BIN_BIT}, Decimal('1.90734863281250000000'), 'Mib'),

            ({'value': 1, 'unit': 'B', 'return_as': 'b'}, 8, 'b'),
            ({'value': 1, 'unit': 'Tb', 'return_as': 'Gb'}, 1000, 'Gb'),
            ({'value': 1, 'unit': 'Gb', 'return_as': 'KB'}, 125000, 'KB'),
            ({'value': 50, 'unit': 'Pb', 'return_as': 'TB'}, 6250, 'TB'),
        ]

        dsc = data_size_calculator
        for test in test_sets:
            tmp_check = dsc(**test[0])

            msg = 'dsc(%r).value = %s, expected: %s  (return:%s)' % (test[0], tmp_check[0], test[1], tmp_check)
            with self.subTest(m=msg):
                self.assertEqual(test[1], tmp_check[0])

            msg = 'dsc(%r).unit = %s, expected: %s  (return:%s)' % (test[0], tmp_check[1], test[2], tmp_check)
            with self.subTest(m=msg):
                self.assertEqual(test[2], tmp_check[1])
