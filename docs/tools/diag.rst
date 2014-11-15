=============================================================
``openxc-diag`` - Send and receive OBD-II diagnostic messages
=============================================================

:program:`openxc-diag` is a command-line tool for adding new recurring or
one-time diagnostic message requests through a vehicle interface.

Perform a single diagnostic request
=================================

This example will add a new one-time diagnostic request - it will be sent
once, and any respones will be printed to the terminal via stdout. The
``--message-id`` and ``--mode`` options are required. This particular request
sends a functional broadcast request (ID ``0x7df``) for the mode 3 service, to
store a "freeze frame". See the Unified Diagnostics Service and On-Board
Diagnostics standards for more information on valid modes.

The ``bus`` option is not required; the VI wlil use its default configured CAN
bus if one is not specified.

.. code-block:: bash

    $ openxc-diag add --message-id 0x7df --mode 0x3

.. note::

    The vehicle interface must be running firmware that supports diagnostic
    requests.

Add a recurring diagnostic request
=====================================

This example will register a new recurring diagnostic request with the vehicle
interface. It will request the OBD-II engine speed parameter at 1Hz, so if you
subseqeuntly run the ``openxc-dump`` command you will be able to read the
responses.

.. code-block:: bash

    $ openxc-diag add --message-id 0x7df --mode 0x1 --pid 0xc --frequency 1

Cancel an existing recurring diagnostic request
===============================================

This example will cancel the recurring diagnostic request we added in the
previous example. Deleting requests also uses the combination of bus, ID, mode
and PID to identify a request.

.. code-block:: bash

    $ openxc-diag cancel --message-id 0x7df --mode 0x1 --pid 0xc

Cancelling a non-recurring diagnostic request
=========================================================

If you're wondering why there are no examples of canceling an existing request
that is not recurring, it's because they either complete or timeout withing 1
second, so there's no reason to try and modify them.

Command-line options
====================

A description overview of all possible command line options can be found via
``--help``.
