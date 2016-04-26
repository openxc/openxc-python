"""
This module contains the methods for the ``openxc-control`` command line
program.

`main` is executed when ``openxc-control`` is run, and all other callables in
this module are internal only.
"""
from __future__ import absolute_import

import argparse
import sys
import time

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device


def version(interface):
    print("Device is running version %s" % interface.version())

def sd_mount_status(interface):
    result = interface.sd_mount_status()
    if(result == 1):
        print("SD card mount status: true")
    else:
        print("SD card mount status: false")		

def device_id(interface):
    print("Device ID is %s" % interface.device_id())

def passthrough(interface, bus, passthrough_enabled):
    if interface.set_passthrough(bus, passthrough_enabled):
        print("Bus %u passthrough set to %s" % (bus, passthrough_enabled))

def af_bypass(interface, bus, bypass):
    if interface.set_acceptance_filter_bypass(bus, bypass):
        if bypass:
            bypass_string = "bypassed"
        else:
            bypass_string = "enabled"
        print("Bus %u AF is now %s" % (bus, bypass_string))

def set_payload_format(interface, payload_format):
    if interface.set_payload_format(payload_format):
        print("Changed payload format to %s" % payload_format)

def set_rtc_time(interface, unix_time):
    if interface.rtc_configuration(unix_time):
        print("Time set to %d" % unix_time)

def write_file(interface, filename):
    first_timestamp = None
    with open(filename, "r") as output_file:
        corrupt_entries = 0
        message_count = 0
        start_time = time.time()
        for line in output_file:
            try:
                parsed_message = JsonFormatter.deserialize(line.encode("utf-8"))
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                corrupt_entries += 1
            else:
                # TODO at the moment it's taking longer to write all of
                # individual CAN messages than the time that actually
                # elapsed in receiving the trace - need to implement
                # batching to speed this up. right now this will never sleep
                # because it's always behind.
                timestamp = parsed_message.get('timestamp', None)
                # TODO this duplicates some code from sources/trace.py
                if timestamp is not None:
                    first_timestamp = first_timestamp or timestamp
                    target_time = start_time + (timestamp - first_timestamp)
                    time.sleep(max(.0002, target_time - time.time()))

                message_count += 1
                interface.write(**parsed_message)
        print("%d lines sent" % message_count)
        if corrupt_entries > 0:
            print("%d invalid lines in the data file were not sent" %
                    corrupt_entries)


def parse_options():
    parser = argparse.ArgumentParser(description="Send control messages to an "
            "attached OpenXC vehicle interface", parents=[device_options()])
    parser.add_argument("command", type=str,
            choices=['version', 'write', 'id', 'set', 'sd_mount_status'])
    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument("--name", action="store", dest="write_name",
            help="name for message write request")
    write_group.add_argument("--id", action="store", dest="write_id",
            help="ID for raw message write request")
    parser.add_argument("--bus", action="store", dest="bus",
            default=1,
            help="CAN bus number for the control request")
    parser.add_argument("--value", action="store", dest="write_value",
            help="optional value for message write request")
    parser.add_argument("--event", action="store", dest="write_event",
            help="optional event for message write request")
    parser.add_argument("--data", action="store", dest="write_data",
            help="data for raw message write request")
    parser.add_argument("--frame-format", action="store",
            dest="write_frame_format",  choices=['standard', 'extended'],
            help="explicit frame format for raw message write request")
    write_group.add_argument("-f", "--write-input-file", action="store",
            dest="write_input_file",
            help="the path to a file with a list of raw or translated "
                    "messages to write to the selected vehicle interface")
    parser.add_argument("--passthrough", action="store_true", default=None,
            dest="passthrough_enabled")
    parser.add_argument("--no-passthrough", action="store_false", default=None,
            dest="passthrough_enabled")
    parser.add_argument("--af-bypass", action="store_true", default=None,
            dest="af_bypass")
    parser.add_argument("--no-af-bypass", action="store_false", default=None,
            dest="af_bypass")
    parser.add_argument("--new-payload-format", action="store", default=None,
            choices=['json', 'protobuf'], dest="new_payload_format")
    parser.add_argument("--time",
            action="store",default=None,
            dest="unix_time")
    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    interface_class, interface_kwargs = select_device(arguments)
    interface = interface_class(**interface_kwargs)
    interface.start()

    if arguments.command == "version":
        version(interface)
    elif arguments.command == "sd_mount_status":
        sd_mount_status(interface)
    elif arguments.command == "id":
        device_id(interface)
    elif arguments.command == "set":
        if arguments.passthrough_enabled is not None:
            passthrough(interface, int(arguments.bus), arguments.passthrough_enabled)
        if arguments.af_bypass is not None:
            af_bypass(interface, int(arguments.bus), arguments.af_bypass)
        if arguments.new_payload_format is not None:
            set_payload_format(interface, arguments.new_payload_format)
        if arguments.unix_time is not None:
            set_rtc_time(interface, int(arguments.unix_time))
    elif arguments.command.startswith("write"):
        if arguments.command == "write":
            if arguments.write_name:
                interface.write(name=arguments.write_name,
                        value=arguments.write_value,
                        event=arguments.write_event)
            elif arguments.write_id:
                if not arguments.write_data:
                    sys.exit("%s requires an id and data" % arguments.command)
                # TODO we should use unhexlify as with the diagnostic command
                # payloads so we can standardize the API and not deal with hex
                # strings in code
                interface.write(bus=int(arguments.bus),
                        id=arguments.write_id,
                        data=arguments.write_data,
                        frame_format=arguments.write_frame_format)
            elif arguments.write_input_file:
                write_file(interface, arguments.write_input_file)
            else:
                sys.exit("%s requires a signal name, message ID or filename" % arguments.command)
    else:
        print("Unrecognized command \"%s\"" % arguments.command)
