import unittest
from data_unit_lookups import *


class TestDCLookups(unittest.TestCase):

    def test_breakout_unitset(self):
        test_sets = [
            (BIN_BIT, [BIN, BIT]),
            (DEC_BIT, [DEC, BIT]),
            (BIN_BYT, [BIN, BYT]),
            (DEC_BYT, [DEC, BYT]),
            (None, []),
            (BIN, [BIN]),
            (BIT, [BIT]),
            (DEC, [DEC]),
            (BYT, [BYT]),
        ]

        for test in test_sets:
            tmp_check = breakout_unitset(test[0])
            for ret in tmp_check:
                msg = 'merge(%r) %s should be in %s' % (test[0], ret, test[1])
                with self.subTest(m=msg):
                    self.assertIn(ret, test[1])


    def test_diff_unitset(self):
        test_sets = [
            ({'a': BIN_BYT, 'b': BIN_BYT}, None),
            ({'a': BIN_BYT, 'b': BIN_BIT}, BYT),
            ({'a': BYT, 'b': DEC_BIT}, BYT),
            ({'a': DEC_BYT, 'b': DEC_BIT}, BYT),
            ({'a': None, 'b': BIN_BYT}, None),
            ({'a': DEC_BYT, 'b': BIN_BIT}, DEC_BYT),
            ({'a': DEC_BYT, 'b': BIN_BYT}, DEC),

            ({'a': BIN_BYT, 'b': BIN}, None),
            ({'a': BIN_BYT, 'b': BYT}, None),
            ({'a': BYT, 'b': BIT}, BYT),
            ({'a': None, 'b': BYT}, None),

            ({'a': None, 'b': None}, None),
        ]

        for test in test_sets:
            tmp_check = diff_unitset(**test[0])
            msg = 'merge(%r).value = %s, expected: %s' % (test[0], tmp_check, test[1])
            with self.subTest(m=msg):
                self.assertEqual(test[1], tmp_check)

    def test_dataset_merge(self):
        test_sets = [
            ({'a': BIN_BYT, 'b': BIN_BYT}, BIN_BYT),
            ({'a': BIN_BYT, 'b': BIN}, BIN_BYT),
            ({'a': BYT, 'b': BIN}, BIN_BYT),
            ({'a': DEC_BIT, 'b': None}, DEC_BIT),
            ({'a': None, 'b': BYT}, BYT),

            ({'a': BIN_BYT, 'b': BIN_BYT, 'force_a': True}, BIN_BYT),
            ({'a': BIN, 'b': DEC_BYT, 'force_a': True}, BIN_BYT),
            ({'a': BYT, 'b': BIT, 'force_a': True}, BYT),
            ({'a': DEC, 'b': BIN, 'force_a': True}, DEC),
            ({'a': None, 'b': BIN, 'force_a': True}, BIN),

            ({'a': None, 'b': None, 'force_a': True}, None),
            ({'a': None, 'b': None}, None),

        ]

        test_raises = [
            {'a': BIN_BYT, 'b': DEC_BYT},
            {'a': BIN_BYT, 'b': DEC},
            {'a': BYT, 'b': BIT},

        ]
        for test in test_sets:
            with self.subTest(t='M', method=test[0], result=test[1]):
                tmp_check = merge_ext_unitsets(**test[0])
                self.assertEqual(test[1], tmp_check)

        for test in test_raises:
            with self.subTest(t='R', method=test):
                with self.assertRaises(AttributeError):
                    tmp_check = merge_ext_unitsets(**test)

