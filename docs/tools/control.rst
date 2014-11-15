========================================
``openxc-control`` options and arguments
========================================

:program:`openxc-control` is a command-line tool that can send control messages
to an attached vehicle interface.

Basic use
=========

--------
version
--------

Print the current firmware version and vehicle platform of the attached CAN
translator:

.. code-block:: bash

    $ openxc-control version

.. note::

    The ``version`` command is not supported by the trace file interface.

------
write
------

Send a request to the vehicle interface to write a message back to the CAN bus. The
``--name`` and ``--value`` options are required when using this command.

.. code-block:: bash

    $ openxc-control write --name turn_signal_status --value left

.. note::

    The ``write`` command is not supported by the trace file interface.

.. note::

    The vehicle interface must be running firmware that supports CAN writes, and
    must allow writing the specific message that you request with
    ``openxc-control``.

Command-line options
====================

An overview of all possible command line options can be found via
``--help``.
