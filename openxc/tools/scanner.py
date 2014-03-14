"""Diagnostic Scantool

    * for each active module
       * add a 1hz recurring tester present
       * for each active service on that module
            * for every possible payload
                * send a request, see what it does - print status
       * add a 1hz recurring tester present
"""
from __future__ import absolute_import

import argparse
import time
from collections import defaultdict

from .common import device_options, configure_logging, select_device

TESTER_PRESENT_MODE = 0x3e

def scan(controller, bus=None, message_id=None):

    # Scan for active modules by sending each a tester presnet
    active_modules = set()
    # using 11-bit IDs
    for arb_id in range(0, 0x7ff):
        response = controller.diagnostic_request(arb_id, TESTER_PRESENT_MODE,
                bus=bus, wait_for_first_response=True, pid=0)
        # TODO if we send requests too quickly we get a pipe error from USB -
        # why?
        time.sleep(.01)
        if response is not None:
            active_modules.append(arb_id)

    # Scan for active services on each active module by sending blank requests
    active_modes = defaultdict(list)
    for active_module in active_modules:
        controller.diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=1)

        for mode in range(1, 0xff):
            response = controller.diagnostic_request(arb_id, mode, bus=bus)
            if response is not None:
                # TODO make sure response isn't negative
                active_modules[arb_id].append(mode)

        controller.diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=0)

    # Scan for what each mode can do and what data it can return by fuzzing the
    # payloads
    for arb_id, active_modes in active_modes.iteritems():
        controller.diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=1)

        for mode in active_modes:
            for payload in range(0, 0xffffffffffffff):
                response = controller.diagnostic_request(arb_id, mode,
                        bus=bus, payload=payload)
                if response is not None:
                    # TODO make sure response isn't negative
                    # TODO print out something?
                    pass

        controller.diagnostic_request(arb_id, TESTER_PRESENT_MODE, bus=bus,
                frequency=0)

def parse_options():
    parser = argparse.ArgumentParser(description="Send diagnostic message requests to an attached VI",
            parents=[device_options()])
    parser.add_argument("--bus")
    parser.add_argument("--message")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    scan(controller, arguments.bus, arguments.message)
