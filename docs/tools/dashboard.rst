==========================================
``openxc-dashboard`` options and arguments
==========================================

:program:`openxc-dashboard` is a command-line tool that displays the current
values of all OpenXC messages simultaneously. The dashboard uses ``curses`` to
draw a basic GUI to the terminal.

Only OpenXC messages in the official public set will be displayed. Unofficial
messages may be received, but will not appear on the dashboard.

For each message type, the dashboard displays:

* Message name
* Last received value
* A simple graph of the current value and the range seen
* Total number received since the program started
* A rough calculation of the frequency the message is sent in Hz

If the terminal window is not wide enough, only a subset of this data will be
displayed. The wider you make the window, the more you'll see. The same goes for
the list of messages - if the window is not tall enough, the message list will
be truncated.

The dashboard also displays some overall summary data:

* Total messages received of any type
* Total amount of data received over the source interface
* Average data rate since the program started

If the number of message types is large, you can scroll up and down the list
with the arrow keys or Page Up / Page Down keys.

This is a screenshot of the dashboard showing all possible columns of data.

.. image:: /_static/dashboard.png

This screenshot shows the dashboard displaying raw CAN messages (the vehicle
interface must have CAN passthrough enabled).

.. image:: /_static/dashboard-raw.png

Basic use
=========

Open the dashboard:

.. code-block:: bash

    $ openxc-dashboard

Use a custom USB device:

.. code-block:: bash

    $ openxc-dashboard --usb-vendor 4424

Use a a vehicle interface connected via serial instead of USB:

.. code-block:: bash

    $ openxc-dashboard --serial --serial-device /dev/ttyUSB1

The ``serial-device`` option is only required if the virtual COM port is
different than the default ``/dev/ttyUSB0``.

Play back a trace file in real-time:

.. code-block:: bash

    $ openxc-dashboard --trace monday-trace.json


Command-line options
====================

A quick overview of all possible command line options can be found via
``--help``.

.. include:: ../_shared/common_cmdoptions.rst
