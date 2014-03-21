"""Common functions for parsing command line arguments, shared with all openxc
command line utilities.
"""
import argparse
import logging

from openxc.sources.trace import TraceDataSource
from openxc.interface import SerialVehicleInterface, UsbVehicleInterface, \
        NetworkVehicleInterface


def device_options():
    parser = argparse.ArgumentParser(add_help=False)
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument("--usb", action="store_true", dest="use_usb",
            default=True,
            help="use a USB-connected vehicle interface as the data source")
    device_group.add_argument("--serial", action="store_true",
            dest="use_serial",
            help="use a serial-connected vehicle interface as the data source")
    device_group.add_argument("--network", action="store_true",
            dest="use_network",
            help="use a network-connected vehicle interface as the data source")
    device_group.add_argument("--trace", action="store", dest="trace_file",
            help="use a pre-recorded OpenXC JSON trace file as the data source")
    parser.add_argument("--usb-vendor",
            action="store",
            dest="usb_vendor",
            help="USB vendor ID for the vehicle interface")
    parser.add_argument("--usb-product",
            action="store",
            dest="usb_product",
            help="USB product ID for the vehicle interface")
    parser.add_argument("--serial-port",
            action="store",
            dest="serial_port",
            help="virtual COM port path for serial vehicle interface")
    parser.add_argument("--serial-baudrate",
            action="store",
            dest="baudrate",
            help="baudrate for serial-connected vehicle interface")
    parser.add_argument("--network-host",
            action="store",
            dest="network_host",
            help="host for networked vehicle interface")
    parser.add_argument("--network-port",
            action="store",
            dest="network_port",
            help="network port for networked vehicle interface")
    parser.add_argument("--log-mode",
            action="store",
            default="off",
            choices=["off", "stderr", "file"],
            dest="log_mode",
            help="record logs to a file or stderr, if available from the interface")
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
    else:
        source_class = UsbVehicleInterface
        source_kwargs = dict(vendor_id=arguments.usb_vendor,
                product_id=arguments.usb_product)

    source_kwargs['log_mode'] = arguments.log_mode
    return source_class, source_kwargs
