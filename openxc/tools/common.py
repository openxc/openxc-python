"""Common functions for parsing command line arguments, shared with all openxc
command line utilities.
"""
import argparse
import logging

from openxc.sources.trace import TraceDataSource
from openxc.interface import SerialVehicleInterface, UsbVehicleInterface, \
        NetworkVehicleInterface, BluetoothVehicleInterface


def device_options():
    parser = argparse.ArgumentParser(add_help=False)
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument("--usb", action="store_true", dest="use_usb",
            default=True,
            help="use a USB-connected VI as the data source")
    device_group.add_argument("--serial", action="store_true",
            dest="use_serial",
            help="use a serial-connected VI as the data source")
    device_group.add_argument("--bluetooth", action="store_true",
            dest="use_bluetooth",
            help="use a Bluetooth-connected VI as the data source")
    device_group.add_argument("--network", action="store_true",
            dest="use_network",
            help="use a network-connected VI as the data source")
    device_group.add_argument("--trace", action="store", dest="trace_file",
            help="use a pre-recorded OpenXC JSON trace file as the data source")
    parser.add_argument("--usb-vendor",
            action="store",
            dest="usb_vendor",
            help="USB vendor ID for the VI")
    parser.add_argument("--usb-product",
            action="store",
            dest="usb_product",
            help="USB product ID for the VI")
    parser.add_argument("--bluetooth-address",
            action="store",
            dest="bluetooth_address",
            help="MAC address of Bluetooth VI. If not provided, will " +
                    "perform a scan and select first device with name " +
                    "matching \"OpenXC-VI-*\"")
    parser.add_argument("--serial-port",
            action="store",
            dest="serial_port",
            help="virtual COM port path for serial VI")
    parser.add_argument("--serial-baudrate",
            action="store",
            dest="baudrate",
            help="baudrate for serial-connected VI")
    parser.add_argument("--network-host",
            action="store",
            dest="network_host",
            help="host for networked VI")
    parser.add_argument("--network-port",
            action="store",
            dest="network_port",
            help="network port for networked VI")
    parser.add_argument("--log-mode",
            action="store",
            default="off",
            choices=["off", "stderr", "file"],
            dest="log_mode",
            help="record logs to a file or stderr, if available from the interface")
    parser.add_argument("--format",
            action="store",
            choices=["json", "protobuf"],
            dest="format",
            help="select the data format for sending and receiving with the VI")
    return parser


def configure_logging(level=logging.WARN):
    logging.getLogger("openxc").addHandler(logging.StreamHandler())
    logging.getLogger("openxc").setLevel(level)

def select_device(arguments):
    if arguments.use_serial:
        source_class = SerialVehicleInterface
        source_kwargs = dict(port=arguments.serial_port,
                baudrate=arguments.baudrate)
    elif arguments.trace_file:
        source_class = TraceDataSource
        source_kwargs = dict(filename=arguments.trace_file)
    elif arguments.use_network:
        source_class = NetworkVehicleInterface
        source_kwargs = dict(host=arguments.network_host,
                port=arguments.network_port)
    elif arguments.use_bluetooth:
        source_class = BluetoothVehicleInterface
        source_kwargs = dict(address=arguments.bluetooth_address)
    else:
        source_class = UsbVehicleInterface
        source_kwargs = dict(vendor_id=arguments.usb_vendor,
                product_id=arguments.usb_product)

    source_kwargs['log_mode'] = arguments.log_mode
    source_kwargs['payload_format'] = arguments.format
    return source_class, source_kwargs
