import argparse
import time

from openxc.formats.json import JsonFormatter
from openxc.sources.usb import UsbDataSource
from openxc.sources.serial import SerialDataSource
from .args import device_options

def receive(message):
    message['timestamp'] = time.time()
    # TODO update docs on trace file format
    print(JsonFormatter.serialize(message))

def parse_options():
    parser = argparse.ArgumentParser(description="Receive and print OpenXC "
        "messages over USB", parents=[device_options()])
    parser.add_argument("--corrupted",
            action="store_true",
            dest="show_corrupted",
            default=False)

    arguments = parser.parse_args()
    return arguments

def main():
    arguments = parse_options()

    if arguments.use_serial:
        source_class = SerialDataSource
        source_kwargs = dict(port=arguments.serial_port,
                baudrate=arguments.baudrate)
    else:
        source_class = UsbDataSource
        source_kwargs = dict(vendor_id=arguments.usb_vendor)

    source = source_class(receive, **source_kwargs)
    source.start()
