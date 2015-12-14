Data Size Calculator
====================

This object handles converting between one unit to another unit.

Notes:
    * All numbers entered will be converted to decimals and all return values are of type :py:class:`decimal.Decimal`
    * Unit names passed must be correct standard abbreviations for the units, (use the :py:class:`DataUnitManager` to normalize
      and validate unit names if needed).

.. autoclass:: data_size_helper.DataSizeHelper

Examples (note, returns are shown as literal int or float, however are actually of type Decimal).:

    >>> from DataSizeHelper import data_size_calculator,
    >>> dsc = data_size_calculator
    >>> dsc(1000, 'Kb', 'Mb')
    (1, 'Mb')
    >>> dsc(1, 'b', 'Kib')
    (1024, 'Kib')
    >>> data_size_calculator(1000, 'Mb', dsc.DEC_BIT)
    (1, 'Gb')

