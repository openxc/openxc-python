"""
This module contains the methods for the ``openxc-control`` command line
program.

`main` is executed when ``openxc-control`` is run, and all other callables in
this module are internal only.
"""
from __future__ import absolute_import

import argparse
import sys

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device


def version(controller):
    print("Device is running version %s" % controller.version())


def reset(controller):
    print("Resetting device...")
    controller.reset()
    version(controller)


def write_file(controller, filename):
    with open(filename, "r") as output_file:
        corrupt_entries = 0
        message_count = 0
        for line in output_file:
            try:
                parsed_message = JsonFormatter.deserialize(line)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                corrupt_entries += 1
            else:
                message_count += 1
                controller.write(parsed_message['name'],
                        parsed_message['value'], parsed_message['event'])
        print("%d lines sent" % message_count)
        if corrupt_entries > 0:
            print("%d invalid lines in the data file were not sent" %
                    corrupt_entries)


def write(controller, name, value, event):
    print("Sending command %s: %s %s" % (name, value, event))
    controller.write(name, value, event)
    print("Done.")


def parse_options():
    parser = argparse.ArgumentParser(description="Send control messages to an "
            "attached OpenXC CAN translator", parents=[device_options()])
    parser.add_argument("command", type=str,
            choices=['version', 'reset', 'write'])
    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument("--name", action="store", dest="write_name",
            help="name for message write request")
    parser.add_argument("--value", action="store", dest="write_value",
            help="option value for message write request")
    parser.add_argument("--event", action="store", dest="write_event",
            help="optional event for message write request")
    write_group.add_argument("-f", "--file", action="store",
            dest="write_input_file",
            help="path to a file with a list of message requests")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)

    if arguments.command == "version":
        version(controller)
    elif arguments.command == "reset":
        reset(controller)
    elif arguments.command == "write":
        if arguments.write_name:
            write(controller, arguments.write_name, arguments.write_value,
                    arguments.write_event)
        elif arguments.write_input_file:
            write_file(controller, arguments.write_input_file)
        else:
            sys.exit("'write' requires at least a name or filename")
    else:
        print("Unrecognized command \"%s\"" % arguments.command)
