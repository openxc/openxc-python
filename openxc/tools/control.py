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
                        parsed_message['value'])
        print("%d lines sent" % message_count)
        if corrupt_entries > 0:
            print("%d invalid lines in the data file were not sent" %
                    corrupt_entries)


def write(controller, name, value):
    print("Sending command %s: %s" % (name, value))
    controller.write(name, value)
    print("Done.")


def parse_options():
    parser = argparse.ArgumentParser(description="Send control messages to an "
            "attached OpenXC CAN translator", parents=[device_options()])
    parser.add_argument("command", type=str,
            choices=['version', 'reset', 'write'])
    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument("--name",
            action="store",
            dest="write_name")
    parser.add_argument("--value",
            action="store",
            dest="write_value")
    write_group.add_argument("-f", "--file",
            action="store",
            dest="write_input_file")

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
            if not arguments.write_value:
                sys.exit("'write' requires a name and value or filename")
            write(controller, arguments.write_name, arguments.write_value)
        elif not arguments.write_input_file:
            sys.exit("'write' requires a name and value or filename")
        else:
            write_file(controller, arguments.write_input_file)
    else:
        print("Unrecognized command \"%s\"" % arguments.command)
