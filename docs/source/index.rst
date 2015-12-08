.. Data Size Helper documentation master file, created by
   sphinx-quickstart on Mon Dec  7 13:42:34 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Data Size Helper's documentation!
============================================

Contents:

.. toctree::
   :maxdepth: 2


There are three main parts to this package:
   * DataUnitManager:
      The DataUnitManager class provides for normalization of unit text and parsing strings into their pieces (value,
      unit, and suffix).
   * DataSizeCalculator:
      The DataSizeCalculator handles converting from one unit to another, If you only need to convert from 'Mb' to 'KB'
      for example, all you would need is the calculator.
   * DataHelper:
      The DataHelper class provides for a flexible object that can be converted from unit to unit, as well as used in
      other calculations and in string formatting of units.  The DataHelper uses DataUnitManager and DataSizeCalculator
      objects.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

