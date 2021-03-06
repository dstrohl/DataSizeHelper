Data Size Helper String Formatting
==================================


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



        Custom Format Syntax (separate keys with ':'):

            [:unitset|:unit][+][:s|:S][:l|:L][:c|:C]

            Unitset or Unit:
                'bb': normalize to binary byte
                'bt': normalize to bin_bit
                'db': normalize to dec_byte
                'dt': normalize to dec_bit
                'n': normalize to defined unitset (if defined)
                <unit short name>: force to unit short name
                'd': use standard defined units
                None/Missing = do not normalize

            '+':
                Forces the use of long names (such as megabyte instead of Mb).

            's' or 'S':
                's': Do not include suffix
                'S': Include suffix ('/s') if defined [default]

            The following are only used if long names are used.
            'l' or 'L':
                'l': Do not pluralize.
                'L': pluralize if long names are used [default]

            'c' or 'C':
                'c': Only use lower case
                'C': Use proper case ('Megabyte') [default]

        examples (using 'MB' unit):

            * {:MB+} = "Megabytes/s"
            * {:bb:S} "
            * {:BB:s:}         "0.195 Kb"
            * {:D:c:l}        '10 gigabyte/s"


