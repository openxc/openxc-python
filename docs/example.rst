Example Code
=============

Read an unfiltered stream of OpenXC messages from a USB vehicle interface:

.. code-block:: python

    from openxc.interface import UsbVehicleInterface

    def receive(message, **kwargs):
        # this callback will receive each message received as a dict
        print(message['name'])

    vi = UsbVehicleInterface(callback=receive)
    vi.start()
    # This will block until the connection dies or you exit the program
    vi.join()

If you want to connect to a Bluetooth interface (currently only supported in
Linux), just replace ``UsbVehicleInterface`` with ``BluetoothVehicleInterface``.

The base ``VehicleInterface`` classes all implement the ``Controller`` API,
which also supports writing CAN messages, creating diagnostic requests and
sending configuration commands to the VI.

For example, to create a diagnostic request and wait for responses:

.. code-block:: python

    message_id = 42
    mode = 1
    bus = 1
    pid = 3

    responses = vi.create_diagnostic_request(message, mode,
            bus=bus, pid=pid, wait_for_first_response=True)

To write a low-level CAN message (the VI must be configured to allow this):

.. code-block:: python

    vi.write(bus=1, id=42, data="0x1234567812345678")

To put the CAN acceptance filter in bypass mode for bus 1:

.. code-block:: python

    vi.set_passthrough(1, true)

There are many more commands and options, and most have documented APIs in the
code base. You are encouraged you to dig around as the library is fairly small
and should be easy to grok. More examples and documentation would be a most
welcome contribution!
