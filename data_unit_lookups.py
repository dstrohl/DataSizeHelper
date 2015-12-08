
DEC_BYT = 'decimal-byte'
DEC_BIT = 'decimal-bit'
BIN_BYT = 'binary-byte'
BIN_BIT = 'binary-bit'
BIT = 'bit'
BYT = 'byte'
BIN = 'binary'
DEC = 'decimal'

# This is also the order that they will be used in various unit guessing operations if no better information is found.
UNITSET_NAMES = [DEC_BYT, DEC_BIT, BIN_BIT, BIN_BYT]

FORCE_AS_NAMES = list(UNITSET_NAMES)
FORCE_AS_NAMES.extend([BIT, BYT, BIN, DEC])

SUFFIX_SETS = [
    {'/s': ['ps', '/s', ' per sec', '/sec', ' per second', '/second', ' / s', ' / sec', ' / second']},
]

UNITSET_INFO = {
    DEC_BIT: {'power': 1000, 'mult': 1, 's_ext': 'b', 'l_ext': BIT, 'bd': DEC, 'bb': BIT},
    DEC_BYT: {'power': 1000, 'mult': 8, 's_ext': 'B', 'l_ext': BYT, 'bd': DEC, 'bb': BYT},
    BIN_BIT: {'power': 1024, 'mult': 1, 's_ext': 'b', 'l_ext': BIT, 'bd': BIN, 'bb': BIT},
    BIN_BYT: {'power': 1025, 'mult': 8, 's_ext': 'B', 'l_ext': BYT, 'bd': BIN, 'bb': BYT}}

EXT_UNITSET_INFO = dict(UNITSET_INFO)
EXT_UNITSET_INFO.update({
    BIN: {'bd': BIN, 'bb': None},
    DEC: {'bd': DEC, 'bb': None},
    BYT: {'bd': None, 'bb': BYT},
    BIT: {'bd': None, 'bb': BIT},
})

DEFAULT_UNITSETS = {
    None: DEC_BYT,
    DEC: DEC_BYT,
    BIN: BIN_BIT,
    BYT: DEC_BYT,
    BIT: DEC_BIT
}

BASEUNITS = dict(
    B=dict(cm=0, dsn='', dln='', bsn='', bln=''),
    K=dict(cm=1, dsn='K', dln='kilo', bsn='Ki', bln='kibi'),
    M=dict(cm=2, dsn='M', dln='mega', bsn='Mi', bln='mebi'),
    G=dict(cm=3, dsn='G', dln='giga', bsn='Gi', bln='gibi'),
    T=dict(cm=4, dsn='T', dln='tera', bsn='Ti', bln='tebi'),
    P=dict(cm=5, dsn='P', dln='peta', bsn='Pi', bln='pebi'),
    E=dict(cm=6, dsn='E', dln='exa', bsn='Ei', bln='exbi'),
    Z=dict(cm=7, dsn='Z', dln='zetta', bsn='Zi', bln='zebi'),
    Y=dict(cm=8, dsn='Y', dln='yotta', bsn='Yi', bln='yobi'),
)


CONVERSION_UNITS = {
    'Eb': 1000000000000000000,
    'Eib': 1152921504606846976,
    'exabit': 1000000000000000000,
    'exbibit': 1152921504606846976,
    'Tb': 1000000000000,
    'Tib': 1099511627776,
    'terabit': 1000000000000,
    'tebibit': 1099511627776,
    'b': 1,
    'bit': 1,
    'Zb': 1000000000000000000000,
    'Zib': 1180591620717411303424,
    'zettabit': 1000000000000000000000,
    'zebibit': 1180591620717411303424,
    'Kb': 1000,
    'Kib': 1024,
    'kilobit': 1000,
    'kibibit': 1024,
    'Pb': 1000000000000000,
    'Pib': 1125899906842624,
    'petabit': 1000000000000000,
    'pebibit': 1125899906842624,
    'Yb': 1000000000000000000000000,
    'Yib': 1208925819614629174706176,
    'yottabit': 1000000000000000000000000,
    'yobibit': 1208925819614629174706176,
    'Gb': 1000000000,
    'Gib': 1073741824,
    'gigabit': 1000000000,
    'gibibit': 1073741824,
    'Mb': 1000000,
    'Mib': 1048576,
    'megabit': 1000000,
    'mebibit': 1048576,
    'EB': 8000000000000000000,
    'EiB': 9223372036854775808,
    'exabyte': 8000000000000000000,
    'exbibyte': 9223372036854775808,
    'TB': 8000000000000,
    'TiB': 8796093022208,
    'terabyte': 8000000000000,
    'tebibyte': 8796093022208,
    'B': 8,
    'byte': 8,
    'ZB': 8000000000000000000000,
    'ZiB': 9444732965739290427392,
    'zettabyte': 8000000000000000000000,
    'zebibyte': 9444732965739290427392,
    'KB': 8000,
    'KiB': 8192,
    'kilobyte': 8000,
    'kibibyte': 8192,
    'PB': 8000000000000000,
    'PiB': 9007199254740992,
    'petabyte': 8000000000000000,
    'pebibyte': 9007199254740992,
    'YB': 8000000000000000000000000,
    'YiB': 9671406556917033397649408,
    'yottabyte': 8000000000000000000000000,
    'yobibyte': 9671406556917033397649408,
    'GB': 8000000000,
    'GiB': 8589934592,
    'gigabyte': 8000000000,
    'gibibyte': 8589934592,
    'MB': 8000000,
    'MiB': 8388608,
    'megabyte': 8000000,
    'mebibyte': 8388608,
}

def opposite_unitset(unitset):
    if unitset is None:
        return None
    elif unitset == BIN_BIT:
        return DEC_BYT
    elif unitset == BIN_BYT:
        return DEC_BIT
    elif unitset == DEC_BIT:
        return BIN_BYT
    elif unitset == DEC_BYT:
        return BIN_BIT
    elif unitset == DEC:
        return BIN
    elif unitset == BIN:
        return DEC
    elif unitset == BYT:
        return BIT
    elif unitset == BIT:
        return BYT
    else:
        raise AttributeError("Invalid unitset passed.")
def breakout_unitset(unitset):
    if unitset is None:
        return []
    tmp_ret = []
    if BIN in unitset:
        tmp_ret.append(BIN)
    if DEC in unitset:
        tmp_ret.append(DEC)
    if BIT in unitset:
        tmp_ret.append(BIT)
    if BYT in unitset:
        tmp_ret.append(BYT)
    return tmp_ret

def diff_unitset(a, b):
    """
    returns the pieces of a that are different from b
    :param a:
    :param b:
    :return:
    """
    if a is None or a == b:
        return None

    out_a = {}
    out_b = {}

    out_a['bb'] = EXT_UNITSET_INFO[a]['bb'] or EXT_UNITSET_INFO[b]['bb']
    out_a['bd'] = EXT_UNITSET_INFO[a]['bd'] or EXT_UNITSET_INFO[b]['bd']
    out_b['bb'] = EXT_UNITSET_INFO[b]['bb'] or EXT_UNITSET_INFO[a]['bb']
    out_b['bd'] = EXT_UNITSET_INFO[b]['bd'] or EXT_UNITSET_INFO[a]['bd']

    tmp_ret_list = []
    if out_a['bd'] != out_b['bd']:
        tmp_ret_list.append(out_a['bd'])
    if out_a['bb'] != out_b['bb']:
        tmp_ret_list.append(out_a['bb'])

    tmp_ret = '-'.join(tmp_ret_list)
    if tmp_ret == '':
        return None
    return tmp_ret


def make_unit_name(base, unitset, long=False):
    unit_info = BASEUNITS[base]
    us_info = UNITSET_INFO[unitset]
    if us_info['bd'] == 'binary':
        if long:
            return unit_info['bln']+us_info['l_ext']
        else:
            return unit_info['bsn']+us_info['s_ext']
    else:
        if long:
            return unit_info['dln']+us_info['l_ext']
        else:
            return unit_info['dsn']+us_info['s_ext']


def merge_ext_unitsets(a, b, force_a=False):
    if a == b:
        return a
    if a is None:
        return b
    if b is None:
        return a

    out_a = {}
    out_b = {}

    if not force_a:

        out_a['bb'] = EXT_UNITSET_INFO[a]['bb'] or EXT_UNITSET_INFO[b]['bb']
        out_a['bd'] = EXT_UNITSET_INFO[a]['bd'] or EXT_UNITSET_INFO[b]['bd']
        out_b['bb'] = EXT_UNITSET_INFO[b]['bb'] or EXT_UNITSET_INFO[a]['bb']
        out_b['bd'] = EXT_UNITSET_INFO[b]['bd'] or EXT_UNITSET_INFO[a]['bd']

        if out_a['bb'] != out_b['bb'] or out_a['bd'] != out_b['bd']:
            raise AttributeError('unitsets contain unmergable attributes (%s / %s)' % (a, b))
    else:

        out_a['bb'] = EXT_UNITSET_INFO[a]['bb'] or EXT_UNITSET_INFO[b]['bb']
        out_a['bd'] = EXT_UNITSET_INFO[a]['bd'] or EXT_UNITSET_INFO[b]['bd']
    tmp_ret_list = []
    if out_a['bd'] is not None:
        tmp_ret_list.append(out_a['bd'])
    if out_a['bb'] is not None:
        tmp_ret_list.append(out_a['bb'])

    tmp_ret = '-'.join(tmp_ret_list)
    return tmp_ret

TO_BIT_CONVERSION = {
    'b': 1,
    'Kb': 1000,
    'Mb': 1000000,
    'Gb': 1000000000,
    'Tb': 1000000000000,
    'Pb': 1000000000000000,
    'Eb': 1000000000000000000,
    'Zb': 1000000000000000000000,
    'Yb': 1000000000000000000000000,
    'B': 8,
    'KB': 8000,
    'MB': 8000000,
    'GB': 8000000000,
    'TB': 8000000000000,
    'PB': 8000000000000000,
    'EB': 8000000000000000000,
    'ZB': 8000000000000000000000,
    'YB': 8000000000000000000000000,
    'Kib': 1024,
    'Mib': 1048576,
    'Gib': 1073741824,
    'Tib': 1099511627776,
    'Pib': 1125899906842620,
    'Eib': 1152921504606850000,
    'Zib': 1180591620717410000000,
    'Yib': 1208925819614630000000000,
    'KiB': 8192,
    'MiB': 8388608,
    'GiB': 8589934592,
    'TiB': 8796093022208,
    'PiB': 9007199254740990,
    'EiB': 9223372036854780000,
    'ZiB': 9444732965739290000000,
    'YiB': 9671406556917030000000000,
}
