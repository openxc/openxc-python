from __future__ import absolute_import

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

    # TODO what format is the payload going to be? hex string?
    response = controller.diagnostic_request(message, mode, bus=bus, pid=pid,
            frequency=frequency, payload=arguments.payload,
            wait_for_first_response=True)
    print(response)


def parse_options():
    parser = argparse.ArgumentParser(
            description="Send diagnostic message requests to an attached VI",
            parents=[device_options()])
    parser.add_argument("--message", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--bus")
    parser.add_argument("--pid")
    parser.add_argument("--payload")
    parser.add_argument("--frequency")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    # wait for the receiving thread to spin up
    time.sleep(.1)

    diagnostic_request(arguments, controller)
