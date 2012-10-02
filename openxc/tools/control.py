import argparse
import time
import sys

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device

def receive(message):
    message['timestamp'] = time.time()
    # TODO update docs on trace file format
    print(JsonFormatter.serialize(message))

def parse_options():
    parser = argparse.ArgumentParser(description="Receive and print OpenXC "
        "messages over USB", parents=[device_options()])
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

def version(controller):
    print("Device is running version %s" % controller.version())

def reset(controller):
    print("Resetting device...")
    controller.reset()
    version()

def write_file(controller, filename):
    with open(filename, "r") as f:
        corrupt_entries = 0
        message_count = 0
        for line in f:
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
    bytes_written = controller.write(name, value)
    print("Done.")


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(receive, **controller_kwargs)

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
