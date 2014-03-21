------------------------
Common interface options
------------------------

These command-line options are common to all of the tools that connect to a CAN
translator.

.. cmdoption:: --usb

    Use a vehicle interface connected via USB as the data source. USB is the
    default data source. This option is mutually exclusive with ``--serial``
    and ``--trace``.

.. cmdoption:: --serial

    Use a vehicle interface connected via a USB-to-serial adapter as the data
    source. This option is mutually exclusive with ``--usb`` and ``--trace``.

.. cmdoption:: --trace <tracefile>

    Use a previously recorded OpenXC trace file as the data source. This option
    is mutually exclusive with ``--usb`` and ``--serial``.

.. cmdoption:: --usb-vendor <vendor_id>

    Specify the USB vendor ID of the attached vehicle interface to use. Defaults to
    the Ford Motor Company vendor ID, ``0x1bc4``.

    If the data source is not set to USB, this option has no effect.

.. cmdoption:: --serial-port <port>

    Specify the path to the virtual COM port of the vehicle interface. Defaults to
    ``/dev/ttyUSB0``.

    If the data source is not set to serial, this option has no effect.

.. cmdoption:: --serial-baudrate <baudrate>

    Specify the baudrate to use with the serial-based vehicle interface. Defaults
    to 115200.

    If the data source is not set to serial, this option has no effect.

