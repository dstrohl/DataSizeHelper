Data Size Concepts
==================

UNITSETS
--------

Unitsets are a key concept for the data size helper, these define how the system handles normalization and string
output.

Unitsets determine:
    * If the system is using decimal or binary math.
    * If the system is assuming bits or bytes.

There are four unitsets used in the DataSizeHelper classes:

+---------+------------------------+----------------------+
|         | BYTES                  | BITS                 |
+=========+========================+======================+
| DECIMAL | DECIMAL-BYTES          | DECIMAL-BITS         |
|         | - example: Megabytes   | - example: Gigabits  |
+---------+------------------------+----------------------+
| BINARY  | BINARY-BYTES           | BINARY-BITS          |
|         | - example: Mibibytes   | - example: Kibibits  |
+---------+------------------------+----------------------+

Differences
+++++++++++

* Each Byte is 8 bits, this does not matter if converting from bytes to bytes, or bits to bits, but keep it in
  mind when going from bits to bytes or vice-versa.
* When using DECIMAL units, the units use base-10 math, so each unit size is 1000 times the last one.
* When using BINARY units, the units use base-2 math, so each unit size is 1024 times the last one.

References
++++++++++
https://en.wikipedia.org/wiki/Units_of_information
