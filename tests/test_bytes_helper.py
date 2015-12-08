import unittest
from data_size_helper import DataSizeHelper
from decimal import Decimal

class TestDSH(unittest.TestCase):

    def test_bits_default_bits(self):
        dsh = DataSizeHelper(default_unit='b')

        tmp_ret = dsh('1B').b
        self.assertEqual(8, tmp_ret)

        tmp_ret = dsh('800b').B
        self.assertEqual(100, tmp_ret)

        tmp_ret = dsh(800).B
        self.assertEqual(100, tmp_ret)

        dsh.b = '1mb'
        self.assertEqual(1, dsh.Mb)

        with self.assertRaises(AttributeError):
            tmp_ret = dsh('blah')


    def test_bytes_strict(self):
        dsh = DataSizeHelper(unit='B')

        tmp_ret = dsh('1B').b
        self.assertEqual(8, tmp_ret)

        tmp_ret = dsh('800 b').B
        self.assertEqual(100, tmp_ret)

        tmp_ret = dsh(800).B
        self.assertEqual(800, tmp_ret)

        dsh.b = '1mb'
        self.assertEqual(1, dsh.Mb)

    def test_setting_with_callables(self):
        dsh = DataSizeHelper()

        dsh.b = 80
        tmp_ret = dsh.B
        self.assertEqual(10, tmp_ret)

    def test_comparison(self):
        dsh = DataSizeHelper(unit='b')

        dsh.b = 800

        self.assertTrue(dsh > 300)
        self.assertTrue(dsh >= 300)
        self.assertTrue(dsh >= 800)

        dsh.unit = 'B'

        self.assertTrue(dsh < 200)
        self.assertTrue(dsh <= 100)
        self.assertTrue(dsh <= '100B')
        self.assertTrue(dsh <= 1000.1)

        dsh.unit = 'Kb'
        self.assertEqual(dsh, Decimal('0.8'))
        self.assertTrue(dsh == Decimal('0.8'))
        self.assertTrue(dsh != 1)

    def test_math(self):
        dsh = DataSizeHelper()

        dsh.b = 80

        tmp_ret = 2 + dsh.b
        self.assertEqual(82, tmp_ret)

        tmp_ret = dsh.b + 1
        self.assertEqual(81, tmp_ret)

        dsh += 1
        self.assertEqual(Decimal('10.125'), dsh.B)

        dsh += 1
        self.assertEqual(Decimal('10.250'), dsh.B)

        dsh += '1 b'
        self.assertEqual(Decimal('10.375'), dsh.B)

        dsh += 1
        self.assertEqual(Decimal('10.5'), dsh.B)

        dsh -= '8B'
        self.assertEqual(Decimal('2.5'), dsh.B)

        '''
        tmp_ret = dsh.b += 1
        self.assertEqual(1.1, tmp_ret.B)

        tmp_ret = dsh.B += 1
        self.assertEqual(2.1, tmp_ret.B)

        tmp_ret = dsh.B += '1 b'
        self.assertEqual(2.2, tmp_ret.B)

        tmp_ret = dsh += 1
        self.assertEqual(2.2, tmp_ret.B)

        tmp_ret = dsh -= '1B'
        self.assertEqual(1.3, tmp_ret.B)
        '''

    def test_str_ret(self):
        dsh = DataSizeHelper()

        dsh.b = 800
        self.assertEqual('100 B', str(dsh.get_str('B')))
        self.assertEqual('800 b', str(dsh))
        self.assertEqual('0.1 KB', str(dsh.get_str('KB')))

    def test_format(self):
        dsh = DataSizeHelper()

        dsh.b = 800
        self.assertEqual('100 B', '{:B:}'.format(dsh))
        self.assertEqual('800 b', '{}'.format(dsh))
        self.assertEqual('0.1000 KB', '{:0.4:KB:}'.format(dsh))

    def test_default_setup(self):
        dsh = DataSizeHelper(unit='KB')
        tmp_ret = dsh(1).B
        self.assertEqual(1000, tmp_ret)

    def test_default_method(self):
        dsh = DataSizeHelper()
        tmp_ret = dsh(8000).KB
        self.assertEqual(8, tmp_ret)
        dsh.default_unit = 'KB'
        tmp_ret = dsh(8000).KB
        self.assertEqual(8000, tmp_ret)

    def test_decimal(self):
        dsh = DataSizeHelper(unit='B')
        dsh.B = 100
        self.assertEqual(Decimal('0.1'), dsh.kB)

        dsh.B -= 99
        self.assertEqual(1, dsh.B)

        dsh *= 1000
        self.assertEqual(1, dsh.KB)

    def test_as_class(self):
        self.assertEqual(8, DataSizeHelper('1B').b)
        self.assertEqual(100, DataSizeHelper('800 b').B)
        self.assertEqual(800, DataSizeHelper(800).B)





if __name__ == '__main__':
    unittest.main()
