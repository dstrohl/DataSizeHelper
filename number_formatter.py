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

"""


def split_numbers(str_in, from_right=False, include=''):
    ret_str = list(str_in[:])
    if not from_right:
        ret_str.reverse()
    num_str = []

    while ret_str and (ret_str[-1].isdigit() or ret_str[-1] in include):
        num_str.append(ret_str.pop())

    if from_right:
        num_str.reverse()
    else:
        ret_str.reverse()

    return ''.join(num_str), ''.join(ret_str)

class GroupGenerator(object):
    def __init__(self, groupings, thousands_sep=','):
        self.groupings = groupings or [3, 0]
        self.cur_index = -1
        self.position = 0
        self.cur_group_size = None
        self.thousands_sep = thousands_sep

    @property
    def next(self):
        self.cur_index += 1
        return self.group(self.cur_index)

    def group(self, index):
        try:
            tmp_ret = self.groupings[index]
        except IndexError:
            index = len(self.groupings)-1
            tmp_ret = self.groupings[index]

        if tmp_ret == locale.CHAR_MAX:
            return 99999
        elif tmp_ret == 0:
            return self.groupings[index-1]
        else:
            return tmp_ret

    def __str__(self):
        if self.cur_group_size is None:
            self.cur_group_size = self.next
        self.position += 1
        if self.position == self.cur_group_size:
            self.position = 0
            self.cur_group_size = self.next
            return self.thousands_sep
        else:
            return ''

class NumberStringHelper(object):
    pre_pad = ''
    pre_sign_cur = ''
    pre_sign = ''
    pre_val_cur = ''
    pre_num_pad = ''
    num = ''
    num_dec = ''
    post_num_pad = ''
    post_val_cur = ''
    post_sign = ''
    post_sign_cur = ''
    post_pad = ''

    positions = [
        'pre_pad',
        'pre_cur_sign',
        'pre_currency',
        'pre_val_sign',
        'pre_num_pad',
        'num',
        'num_dec',
        'post_num_pad',
        'post_val_sign',
        'post_currency',
        'post_cur_sign',
        'post_pad']

    def __init__(self):
        for pos in self.positions:
            setattr(self, pos, '')

    def __str__(self):
        tmp_ret = []
        for pos in self.positions:
            tmp_ret.append(getattr(self, pos))
        return ''.join(tmp_ret)

    def __len__(self):
        return len(str(self))

def text_find_and_remove(in_list, *find_char,
                         inc_previous_char=False,
                         get_post_numbers=False,
                         default=None,
                         true_if_match=False,
                         expected_pos=None):
    if in_list:
        for f in find_char:
            try:
                #if expected_pos is not None:
                #    if in_list[expected_pos] == f:
                #        index = expected_pos
                #    else:
                #        continue
                #else:
                index = in_list.index(f)
            except (ValueError, IndexError):
                tmp_ret = default
            else:
                tmp_ret = in_list.pop(index)
                if inc_previous_char:
                    if index > 0:
                        tmp_ret = (tmp_ret, in_list.pop(index-1))
                    else:
                        tmp_ret = (tmp_ret, ' ')
                elif get_post_numbers:
                    num_str = []
                    try:
                        while in_list and in_list[index].isdigit():
                            num_str.append(in_list.pop(index))
                    except IndexError:
                        pass
                    tmp_ret = ''.join(num_str)
                elif true_if_match:
                    tmp_ret = True
                return tmp_ret
    if true_if_match:
        return False
    else:
        return default


def text_number_formatter(value,
                          format_spec=None,
                          fill_char=' ',
                          align='>',
                          sign_type='-',
                          alternate_form=False,
                          inc_thousands_sep=False,
                          use_monentary_format=False,
                          use_international_format=False,
                          width=0,
                          zero_padding=False,
                          precision=6,
                          zero_padding_size=0,
                          use_locale=None,
                          overflow=True,
                          overflow_char='#'):
    """
    format spec:
    [[fill_char]align_type][sign_type][#][0][width][,][$][*zero_prefix_size][.precision]

    :param Decimal value:
    :param str format_spec:
    :param str fill_char:
    :param str align:
    :param str sign_type: std + '(' for put negs in parens
    :param str alternate_form:
    :param bool inc_thousands_sep:
    :param bool use_monentary_format:
    :param bool use_international_format:
    :param int width:
    :param bool zero_padding:
    :param int precision:
    :param int zero_padding_size:
    :param str use_locale:
    :param bool overflow:
    :param str overflow_char:
    :return:
    :rtype: str
    """

    if format_spec is not None and format_spec != '':
        format_spec = list(format_spec)

        if len(format_spec) > 1 and format_spec[1] in '<>=^':
            fill_char = format_spec[0]
            align = format_spec[1]
            format_spec = format_spec[2:]

        elif format_spec[0] in '<>=^':
            align = format_spec[0]
            format_spec = format_spec[1:]



        # align, fill_char = text_find_and_remove(format_spec, *'<>=^', inc_previous_char=True,
        #                                         default=(align, fill_char), expected_pos=1)
        sign_type = text_find_and_remove(format_spec, *'+- ()', default=sign_type)
        alternate_form = text_find_and_remove(format_spec, '#', true_if_match=True)
        use_monentary_format = text_find_and_remove(format_spec, '$', true_if_match=True)
        inc_thousands_sep = text_find_and_remove(format_spec, ',', true_if_match=True)
        zero_padding_size = int(text_find_and_remove(format_spec, '*', get_post_numbers=True, default=zero_padding_size))
        precision = int(text_find_and_remove(format_spec, '.', get_post_numbers=True, default=precision))

        if format_spec:
            if format_spec[0] == '0':
                zero_padding = True
                format_spec = format_spec[1:]
        if format_spec:
            format_spec = ''.join(format_spec)
            try:
                width = int(format_spec)
            except ValueError:
                raise AttributeError('Invalid format spec, %s remaining after parsing' % format_spec)

        '''
        if format_spec[1] in '<>=^':
            fill_char = format_spec[0]
            align = format_spec[1]

            format_spec = format_spec[2:]

        if format_spec[0] in '+- ()':
            sign_type = format_spec[0]
            format_spec = format_spec[1:]

        if format_spec[0] == '#':
            alternate_form = True
            format_spec = format_spec[1:]

        if format_spec[0] == '0':
            zero_padding = True
            format_spec = format_spec[1:]

        if format_spec[0].isdecimal():
            width_str, format_spec = split_numbers(format_spec)
            width = int(width_str)

        if format_spec[0] == ',':
            inc_thousands_sep = True
            format_spec = format_spec[1:]

        if format_spec[0] == '$':
            use_monentary_format = True
            format_spec = format_spec[1:]

        if format_spec[0] == '*':
            zero_padding_size, format_spec = split_numbers(format_spec)
            zero_padding_size = int(zero_padding_size)

        if format_spec[0] == '.':
            precision, format_spec = split_numbers(format_spec)
            if precision == '':
                precision = 0
            else:
                precision = int(precision)
        '''

    if not isinstance(value, Decimal):
        value = Decimal(value)

    if zero_padding:
        zero_padding = '0'
    else:
        zero_padding = ''

    # localized information:
    if use_locale is not None:
        locale.setlocale(locale.LC_ALL, use_locale)
    loc_format = locale.localeconv()

    if use_monentary_format:
        grouping = loc_format['mon_grouping']
        dec_sym = loc_format['mon_decimal_point']
        thou_sym = loc_format['mon_thousands_sep']
        if use_international_format:
            precision = loc_format['int_frac_digits']
        else:
            precision = loc_format['frac_digits']
    else:
        if inc_thousands_sep:
            grouping = loc_format['grouping']
        else:
            grouping = [9999, 0]
        dec_sym = loc_format['decimal_point']
        thou_sym = loc_format['thousands_sep']

    sep_generator = GroupGenerator(grouping, thousands_sep=thou_sym)

    q = Decimal(10) ** -precision      # 2 places --> '0.01'
    has_sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = list(map(str, digits))
    build, next = result.append, digits.pop
    num_str = NumberStringHelper()

    for i in range(precision):
        build(next() if digits else zero_padding)

    if precision:
        build(dec_sym)
        num_str.num_dec = ''.join(reversed(result))
        result.clear()
        if not zero_padding:
            num_str.num_dec = num_str.num_dec.rstrip('.0')
            if align == '=':
                num_str.num_dec = num_str.num_dec.ljust(precision+1, fill_char)
    elif alternate_form:
        num_str.num_dec = '.'

    digit_size = len(digits)
    if not digits:
        build('0')
    elif digit_size < zero_padding_size:
        for i in range(zero_padding_size-digit_size):
            digits.insert(0, '0')

    while digits:
        build(next())
        build(str(sep_generator))

    tmp_number = ''.join(reversed(result))

    num_str.num = tmp_number.lstrip(',')

    if use_monentary_format:
        if use_international_format:
            cur_sym = loc_format['int_curr_symbol']
        else:
            cur_sym = loc_format['currency_symbol']

        if has_sign:
            if loc_format['n_sep_by_space'] or use_international_format:
                cur_space = ' '
            else:
                cur_space = ''

            if loc_format['n_cs_precedes']:
                num_str.pre_currency = cur_sym + cur_space
            else:
                num_str.post_currency = cur_space + cur_sym

            sign_pos = loc_format['n_sign_posn']
            sign_sym = loc_format['negative_sign']
            if sign_pos == 0:
                num_str.pre_cur_sign = '('
                num_str.post_cur_sign = ')'
            elif sign_pos == 1:
                num_str.pre_cur_sign = sign_sym
            elif sign_pos == 2:
                num_str.post_cur_sign = sign_sym
            elif sign_pos == 3:
                num_str.pre_val_sign = sign_sym
            elif sign_pos == 4:
                num_str.post_val_sign = sign_sym
        else:
            if loc_format['p_sep_by_space'] or use_international_format:
                cur_space = ' '
            else:
                cur_space = ''

            if loc_format['p_cs_precedes']:
                num_str.pre_currency = cur_sym + cur_space
            else:
                num_str.post_currency = cur_space + cur_sym

            sign_pos = loc_format['p_sign_posn']
            sign_sym = loc_format['positive_sign']
            if sign_pos == 0:
                num_str.pre_cur_sign = '('
                num_str.post_cur_sign = ')'
            elif sign_pos == 1:
                num_str.pre_cur_sign = sign_sym
            elif sign_pos == 2:
                num_str.post_cur_sign = sign_sym
            elif sign_pos == 3:
                num_str.pre_val_sign = sign_sym
            elif sign_pos == 4:
                num_str.post_val_sign = sign_sym

    else:
        if alternate_form:
            sign_space = ' '
        else:
            sign_space = ''
        if has_sign:
            if sign_type == ' ' or sign_type == '-':
                num_str.pre_val_sign = '-'+sign_space

            elif sign_type == '(':
                num_str.pre_val_sign = '('
                num_str.post_val_sign = ')'
        else:
            if sign_type == '+':
                num_str.pre_val_sign = '+'+sign_space
            elif sign_type == ' ':
                num_str.pre_val_sign = ' '+sign_space



    if width > 0:
        tmp_num_len = len(num_str)
        if tmp_num_len > width and not overflow:
            return ''.ljust(width, overflow_char)

        rem_width = width - tmp_num_len
        pre_pad = ''
        post_pad = ''

        if align == '=' or align == '>':
            pre_pad = ''.ljust(rem_width, fill_char)
        elif align == '<':
            post_pad = ''.ljust(rem_width, fill_char)

        elif align == '^':
            split_width = int(rem_width/2)
            pre_pad = ''.ljust(split_width, fill_char)
            if split_width * 2 == rem_width:
                post_pad = ''.ljust(split_width, fill_char)
            else:
                post_pad = ''.ljust(split_width+1, fill_char)

        if alternate_form:
            num_str.pre_num_pad = pre_pad
            num_str.post_num_pad = post_pad
        else:
            num_str.pre_pad = pre_pad
            num_str.post_pad = post_pad

    return str(num_str)
