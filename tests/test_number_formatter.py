import unittest
import locale
from number_formatter import *

tnf = text_number_formatter

class TestGroupGen(unittest.TestCase):

    def test_group(self):
        gg = GroupGenerator([3, 4, 5, locale.CHAR_MAX, 0])
        self.assertEqual(3, gg.group(0))
        self.assertEqual(4, gg.group(1))
        self.assertEqual(5, gg.group(2))
        self.assertEqual(99999, gg.group(3))
        self.assertEqual(127, gg.group(4))

    def test_next(self):
        gg = GroupGenerator([3, 4, 5, 0])
        self.assertEqual(3, gg.next)
        self.assertEqual(4, gg.next)
        self.assertEqual(5, gg.next)
        self.assertEqual(5, gg.next)
        self.assertEqual(5, gg.next)

    def test_str(self):
        gg = GroupGenerator([1,2,3,0])
        tmp_str = ''

        for i in range(10):
            tmp_str += '0'
            tmp_str += str(gg)

        self.assertEqual('0,00,000,000,0', tmp_str)


class TestNumberFormatter(unittest.TestCase):

    def test_basic_formatting(self):
        test_str = '123456789.1234567'

        self.assertEqual('123456789.1234567', tnf(test_str, precision=10))
        self.assertEqual('123,456,789.123457', tnf(test_str, inc_thousands_sep=True))
        self.assertEqual('123456789.12346', tnf(test_str, precision=5))

    def test_with_signs(self):

        self.assertEqual('-12345.1234', tnf('-12345.1234'))
        self.assertEqual('(12345.1234)', tnf('-12345.1234', sign_type='('))
        self.assertEqual(' 12345.1234', tnf('12345.1234', sign_type=' '))
        self.assertEqual('-12345.1234', tnf('-12345.1234', sign_type=' '))
        self.assertEqual('+12345.1234', tnf('12345.1234', sign_type='+'))

    def test_with_money(self):

        self.assertEqual('($12,345.12)', tnf('-12345.1234', use_monentary_format=True))
        self.assertEqual('$12,345.12', tnf('12345.1234', use_monentary_format=True))
        self.assertEqual('USD 12,345.12', tnf('12345.1234', use_monentary_format=True, use_international_format=True))

    def test_zero_padding(self):
        self.assertEqual('123.123000', tnf('123.123', precision=6, zero_padding=True))
        self.assertEqual('123.12', tnf('123.123', precision=2, zero_padding=True))
        self.assertEqual('000123.123000', tnf('123.123', precision=6, zero_padding=True, zero_padding_size=6))
        self.assertEqual('000,123.123000', tnf('123.123', precision=6, zero_padding=True, zero_padding_size=6, inc_thousands_sep=True))
        self.assertEqual('123.123000', tnf('123.123', precision=6, zero_padding=True, zero_padding_size=1))

    def test_width(self):
        self.assertEqual('    23.123', tnf('23.123', width=10))
        self.assertEqual('  23.123  ', tnf('23.123', width=10, align='^'))
        self.assertEqual('   23.123 ', tnf('23.123', width=10, align='=', precision=4))
        self.assertEqual('===23.123=', tnf('23.123', width=10, align='=', precision=4, fill_char='='))
        self.assertEqual('23.123    ', tnf('23.123', width=10, align='<'))
        self.assertEqual('23.123', tnf('23.123', width=4))

    def test_overflow(self):
        self.assertEqual(' 23.123', tnf('23.123', width=7, overflow=False))
        self.assertEqual('#######', tnf('123456.12', width=7, overflow=False))
        self.assertEqual('-------', tnf('123456789', width=7, overflow=False, overflow_char='-'))

    def test_width_alternate(self):
        self.assertEqual('-   23.123', tnf('-23.123', width=10, alternate_form=True))
        self.assertEqual('    23.123', tnf('23.123', width=10, alternate_form=True))
        self.assertEqual('(  23.123)', tnf('-23.123', width=10, alternate_form=True, sign_type='('))
        self.assertEqual('-  23.123 ', tnf('-23.123', width=10, align='^', alternate_form=True))
        self.assertEqual('-  23.123 ', tnf('-23.123', width=10, align='=', precision=4, alternate_form=True))
        self.assertEqual('- =23.123=', tnf('-23.123', width=10, align='=', precision=4, fill_char='=', alternate_form=True))
        self.assertEqual('- 23.123  ', tnf('-23.123', width=10, align='<', alternate_form=True))
        self.assertEqual('- 23.123', tnf('-23.123', width=4, alternate_form=True))

    def test_width_alternate_money(self):
        self.assertEqual('($  23.12)', tnf('-23.123', width=10, alternate_form=True, use_monentary_format=True))
        self.assertEqual('USD  23.12', tnf('23.123', width=10, alternate_form=True, use_monentary_format=True, use_international_format=True))

    # Repeat formatting with formatting codes

    def test_spec_basic_formatting(self):
        test_str = '123456789.1234567'

        self.assertEqual('123456789.1234567', tnf(test_str, format_spec='.10'))
        self.assertEqual('123,456,789.123457', tnf(test_str, format_spec=','))
        self.assertEqual('123456789.12346', tnf(test_str, format_spec='.5'))

    def test_spec_with_signs(self):

        self.assertEqual('-12345.1234', tnf('-12345.1234'))
        self.assertEqual('(12345.1234)', tnf('-12345.1234', format_spec='('))
        self.assertEqual(' 12345.1234', tnf('12345.1234', format_spec=' '))
        self.assertEqual('-12345.1234', tnf('-12345.1234', format_spec=' '))
        self.assertEqual('+12345.1234', tnf('12345.1234', format_spec='+'))

    def test_spec_with_money(self):

        self.assertEqual('($12,345.12)', tnf('-12345.1234', format_spec='$'))
        self.assertEqual('$12,345.12', tnf('12345.1234', format_spec='$'))

    def test_spec_zero_padding(self):
        self.assertEqual('123.123000', tnf('123.123', format_spec='0.6'))
        self.assertEqual('123.123000', tnf('123.12300', format_spec='0.6'))
        self.assertEqual('000123.123000', tnf('123.123', format_spec='0*6.6'))
        self.assertEqual('000,123.123000', tnf('123.123', format_spec=',0*6.6'))
        self.assertEqual('123.123000', tnf('123.123', format_spec='0*1.6'))

    def test_spec_width(self):
        self.assertEqual('    23.123', tnf('23.123', format_spec='10'))
        self.assertEqual('  23.123  ', tnf('23.123', format_spec='^10'))
        self.assertEqual('    23.123', tnf('23.123', format_spec='10.4'))
        self.assertEqual('===23.123=', tnf('23.123', format_spec='==10#.4'))
        self.assertEqual('23.123    ', tnf('23.123', format_spec='<10',))
        self.assertEqual('23.123', tnf('23.123', format_spec='4'))

    def test_spec_width_alternate(self):
        self.assertEqual('-   23.123', tnf('-23.123', format_spec='#10'))
        self.assertEqual('    23.123', tnf('23.123', format_spec='#10'))
        self.assertEqual('-  23.123 ', tnf('-23.123', format_spec='^#10'))
        self.assertEqual('-  23.123 ', tnf('-23.123', format_spec='=#10.4'))
        self.assertEqual('- =23.123=', tnf('-23.123', format_spec='==#10.4'))
        self.assertEqual('- 23.123  ', tnf('-23.123', format_spec='<#10'))
        self.assertEqual('- 23.123', tnf('-23.123', format_spec='4#'))

    def test_spec_width_alternate_money(self):
        self.assertEqual('($  23.12)', tnf('-23.123', format_spec='#$10'))
