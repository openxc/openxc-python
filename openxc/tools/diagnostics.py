"""
This module contains the methods for the ``openxc-diag`` command line
program.

`main` is executed when ``openxc-diag`` is run, and all other callables in
this module are internal only.
"""


import binascii
import argparse
import time

from .common import device_options, configure_logging, select_device

def diagnostic_request(arguments, controller):
    message = int(arguments.message, 0)
    mode = int(arguments.mode, 0)

    bus = None
    if arguments.bus is not None:
        bus = int(arguments.bus, 0)

    pid = None
    if arguments.pid is not None:
        pid = int(arguments.pid, 0)

    frequency = None
    if arguments.frequency is not None:
        frequency = int(arguments.frequency, 0)

    payload = bytearray()
    if arguments.payload is not None:
        payload = binascii.unhexlify(arguments.payload.split("0x")[1])

    if arguments.command == "add":
        responses = controller.create_diagnostic_request(message, mode, bus=bus,
                pid=pid, frequency=frequency, payload=payload,
                wait_for_first_response=True)
        if len(responses) == 0:
            print("No response received before timeout")
        else: 
            for response in responses:
                # After sending a diagnostic request, it will return with a signal message saying if the
                # request was recieved. After that it used to show about 30 vehicle messages (rpm, speed, etc)
                # with the actual diagnostic response mixed in. So, if the response length is more than
                # 1, it's the response, if its less (only 1) it's the recieved message.
                if len(response) > 1:
                    # Stripping all of the unnesseary data we get after sending a diag request in python
                    # Just like in enabler, it's a diag response if it contains the keys "mode", "bus", 
                    # "id", and "success". 
                    diagMsgReqKeys = ['mode', 'bus', 'id', 'success']
                    indices = [i for i, s in enumerate(response) if all(x in s for x in diagMsgReqKeys)]
                    if indices:
                        print(("Response: %s" % response[indices[0]]))
                else:
                    print(("Response: %s" % response))
    elif arguments.command == "cancel":
        if controller.delete_diagnostic_request(message, mode, bus=bus,
                pid=pid):
            print("Diagnostic request deleted successfully")
        else:
            print("Error when attempting delete")


def parse_options():
    parser = argparse.ArgumentParser(
            description="Sends a diagnostic message request to a vehicle interface",
            parents=[device_options()])
    parser.add_argument("command", type=str, choices=['add', 'cancel'])
    # TODO need to be able to specify name, factor, offset. Needs to be
    # supported in the controller, too.
    parser.add_argument("--message", required=True, help="CAN message ID for the request")
    parser.add_argument("--mode", required=True, help="Diagnostic mode (or service) number")
    parser.add_argument("--bus", help="CAN bus controller address to send on")
    parser.add_argument("--pid", help="Parameter ID (e.g. for Mode 1 request")
    parser.add_argument("--payload", help="A byte array as a hex string to send as payload, e.g. 0x123")
    parser.add_argument("--frequency", help="Frequency (Hz) to repeat this request. If omitted or 0, it will be a one-time request.")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    diagnostic_request(arguments, controller)
    controller.stop()
