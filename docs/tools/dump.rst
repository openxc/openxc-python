=====================================
``openxc-dump`` options and arguments
=====================================

:program:`openxc-dump` is a command-line tool to view the raw data stream from
an attached CAN translator or trace file. It attempts to read OpenXC messages
from the interface specified at the command line (USB, serial or a trace file)
and prints each message received to ``stdout``.

Basic use
=========

View everything:

.. code-block:: bash

    $ openxc-dump

View only a particular message:

.. code-block:: bash

    $ openxc-dump | grep steering_wheel_angle


Use a custom USB device:

.. code-block:: bash

    $ openxc-dump --usb-vendor 4424

Use a a CAN translator connected via serial instead of USB:

.. code-block:: bash

    $ openxc-dump --serial --serial-device /dev/ttyUSB1

The ``serial-device`` option is only required if the virtual COM port is
different than the default ``/dev/ttyUSB0``.

Play back a trace file in real-time:

.. code-block:: bash

    $ openxc-dump --trace monday-trace.json


Command-line options
====================

A quick overview of all possible command line options can be found via
``--help``.

.. cmdoption:: --corrupted

    Dump unparseable messages (assumed to be corrupted) in addition to valid
    messages.

.. include:: _common_cmdoptions.rst
