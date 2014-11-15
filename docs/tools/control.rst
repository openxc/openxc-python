=====================================================================
``openxc-control`` - write messages to the VI and change its settings
=====================================================================

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

---
id
---

Print the unique ID of the VI, if it has one. This is often the MAC address of
the Bluetooth module.

.. code-block:: bash

    $ openxc-control id

---
set
---

Modify the run-time configuration of the VI. Currently, you can change the
acceptance filter (AF) bypass status, passthrough CAN message output, and the
payload format used from the OpenXC message format.

Enable and disable CAN AF bypass for a bus:

.. code-block:: bash

    $ openxc-control set --bus 1 --af-bypass
    $ openxc-control set --bus 1 --no-af-bypass

Enable and disable passthrough of CAN messages to the output interface (e.g. USB
or Bluetooth):

.. code-block:: bash

    $ openxc-control set --bus 1 --passthrough
    $ openxc-control set --bus 1 --no-passthrough

Change the payload format to Protocol Buffers, then back to JSON:

.. code-block:: bash

    $ openxc-control set --new-payload-format json
    $ openxc-control set --new-payload-format protobuf

------
write
------

Send a write request to the VI, either for a simple vehicle message write (to be
translated by the VI to a CAN message), or a raw CAN message.

To write a simple vehicle message, the ``--name`` and ``--value`` parameters are
required. The ``--event`` parameter is optional.

.. code-block:: bash

    $ openxc-control write --name turn_signal_status --value left

To write a CAN messages, the ``--bus``, ``--id`` and ``--data`` parameters are
required. ``data`` should be a hex string.

.. code-block:: bash

    $ openxc-control write --bus 1 --id 0x124 --data 0x0234567812345678

A CAN message with an ID greater than can be represented with 11 bits
will automatically be sent using the extended frame format. If you want to send
a message with a lower ID using the extended frame format, you can use the
``--frame-format`` flag:

.. code-block:: bash

    $ openxc-control write --bus 1 --id 0x124 --data 0x0234567812345678 --frame-format extended

.. note::

    The vehicle interface must be running firmware that supports CAN writes, and
    must allow writing the specific message that you request with
    ``openxc-control``.

Command-line options
====================

An overview of all possible command line options can be found via
``--help``.
