Unitsets
========

Unitsets are a key concept for the data size helper, these define how the system handles normalization and string
output.

Unitsets determine:
    * If the system is using decimal or binary math.
    * If the system is assuming bits or bytes.

There are four unitsets used in the DataSizeHelper classes:

+=========+================+==============+
|         | BYTES          | BITS         |
+=========+================+==============+
| DECIMAL | DECIMAL-BYTES: | DECIMAL-BITS |
|         | ex:Megabytes   | ex:Gigabits  |
+---------+----------------+--------------+
| BINARY  | BINARY-BYTES   | BINARY-BITS  |
|         | ex:Mibibytes   | ex:Kibibits  |
+---------+----------------+--------------+

