"""
This module contains the methods for the ``openxc-diag`` command line
program.

`main` is executed when ``openxc-diag`` is run, and all other callables in
this module are internal only.
"""
from __future__ import absolute_import

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

    response = controller.diagnostic_request(message, mode, bus=bus, pid=pid,
            frequency=frequency, payload=payload,
            wait_for_first_response=True)
    print(response)


def parse_options():
    parser = argparse.ArgumentParser(
            description="Sends a diagnostic message request to a vehicle interface",
            parents=[device_options()])
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
