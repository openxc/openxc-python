"""
This module contains the methods for the ``openxc-scanner`` command line
program.

`main` is executed when ``openxc-scanner`` is run, and all other callables in this
module are internal only.
"""
from __future__ import absolute_import

import argparse
from collections import defaultdict

from .common import device_options, configure_logging, select_device

TESTER_PRESENT_MODE = 0x3e
TESTER_PRESENT_PAYLOAD = bytearray([0])

def scan(controller, bus=None, message_id=None):
    message_ids = []
    if message_id is not None:
        message_ids.append(message_id)
    else:
        # using 11-bit IDs
        message_ids = range(0, 0x7ff + 1)

    print("Sending tester present message to find valid modules arb IDs")
    active_modules = set()
    for arb_id in message_ids:
        response = controller.create_diagnostic_request(arb_id, TESTER_PRESENT_MODE,
                bus=bus, wait_for_first_response=True,
                payload=TESTER_PRESENT_PAYLOAD)
        if response is not None:
            print("0x%x responded to tester present: %s" % (arb_id, response))
            active_modules.add(arb_id)

    # Scan for active services on each active module by sending blank requests
    print("Scanning for services on active modules")
    active_modes = defaultdict(list)
    for active_module in active_modules:
        controller.create_diagnostic_request(active_module, TESTER_PRESENT_MODE,
                bus=bus, frequency=1, wait_for_first_response=True,
                payload=TESTER_PRESENT_PAYLOAD)
        # TODO don't really care about response, but need to wait before sending
        # the next request or we will get a pipe error on USB

        print("Scanning services on 0x%x" % active_module)
        for mode in range(1, 0xff):
            # TODO should we be sending blank requests to each mode, or should
            # we send tester present with the service ID specified?
            response = controller.create_diagnostic_request(active_module, mode, bus=bus,
                    wait_for_first_response=True)
            if response is not None:
                print("0x%x responded on service 0x%x" % (active_module, mode))
                # TODO make sure response isn't negative
                active_modes[active_module].append(mode)

        controller.create_diagnostic_request(active_module, TESTER_PRESENT_MODE, bus=bus,
                frequency=0)

    # Scan for what each mode can do and what data it can return by fuzzing the
    # payloads
    print("Fuzzing the valid modes on acitve modules to see what happens")
    for arb_id, active_modes in active_modes.iteritems():
        controller.create_diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=1, payload=TESTER_PRESENT_PAYLOAD)

        for mode in active_modes:
            # TODO how to support more payloads efficiently?
            for payload in range(0, 0xfffff):
                response = controller.create_diagnostic_request(arb_id, mode,
                        bus=bus, payload=payload, wait_for_first_response=True)
                if response is not None:
                    # TODO make sure response isn't negative
                    # TODO print out something?
                    print("0x%x responded to mode 0x%x request with payload 0x%x with: %s" % (arb_id, mode, payload, response))

        controller.create_diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=0)

def parse_options():
    parser = argparse.ArgumentParser(description="Send diagnostic message requests to an attached VI",
            parents=[device_options()])
    parser.add_argument("--bus", help="CAN bus controller address to send on")
    parser.add_argument("--message-id", help="CAN message ID for the request")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    scan(controller, arguments.bus, arguments.message_id)
