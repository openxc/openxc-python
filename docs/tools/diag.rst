========================================
``openxc-diag`` options and arguments
========================================

:program:`openxc-diag` is a command-line tool for adding new recurring or
one-time diagnostic message requests through a vehicle interface.

Make a single diagnostic request
=================================

This example will create a new one-time diagnostic request - it will be sent
once, and any respones will be printed to the terminal via stdout. The
``--message-id`` and ``--mode`` options are required. This sends a functional
broadcast request (ID ``0x7df``) for the mode 3 service, to store a "freeze
frame". See the Unified Diagnostics Service and On-Board Diagnostics standards
for more information on valid modes.

The ``bus`` option is not required, and the VI will use whatever its configured
default CAN bus if one is not specified.

.. code-block:: bash

    $ openxc-diag --message-id 0x7df --mode 0x3

.. note::

    The vehicle interface must be running firmware that supports diagnostic
    requests.

Create a recurring diagnostic request
=====================================

This example will register a new recurring diagnostic request with the vehicle
interface. It will request the OBD-II engine speed parameter at 1Hz, so if you
subseqeuntly run the ``openxc-dump`` command you will be able to read the
responses.

.. code-block:: bash

    $ openxc-diag --message-id 0x7df --mode 0x1 --pid 0xc --frequency 1


Command-line options
====================

A description overview of all possible command line options can be found via
``--help``.
