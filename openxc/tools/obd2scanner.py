"""
This module contains the methods for the ``openxc-obd2scanner`` command line
program.

`main` is executed when ``openxc-obd2scanner`` is run, and all other callables in this
module are internal only.
"""


import argparse

from .common import device_options, configure_logging, select_device

def scan(controller, bus=None):

    # TODO could read the response from the "PIDs supported" requests to see
    # what the vehicle reports that it *should* support.
    print("Beginning sequential scan of all OBD-II PIDs")
    for pid in range(0, 0x88):
        response = controller.create_diagnostic_request(0x7df, mode=0x1, bus=bus,
                wait_for_first_response=True, pid=pid)
        if response is not None:
            print(("PID 0x%x responded with: %s" % (pid, response)))
        else:
            print(("PID 0x%x did not respond" % pid))

def parse_options():
    parser = argparse.ArgumentParser(description="Send requests for all "
                "OBD-II PIDs sequentially to see what actually responds",
            parents=[device_options()])
    parser.add_argument("--bus")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)
    controller.start()

    scan(controller, arguments.bus)
