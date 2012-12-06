import argparse
import logging

from openxc.sources.trace import TraceDataSource
from openxc.interface import SerialVehicleInterface, UsbVehicleInterface


def device_options():
    parser = argparse.ArgumentParser(add_help=False)
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument("--usb", action="store_true", dest="use_usb",
            default=True,
            help="use a USB-connected CAN translator as the data source")
    device_group.add_argument("--serial", action="store_true",
            dest="use_serial",
            help="use a serial-connected CAN translator as the data source")
    device_group.add_argument("--trace", action="store", dest="trace_file")
    parser.add_argument("--usb-vendor",
            action="store",
            dest="usb_vendor",
            help="USB vendor ID for the CAN translator")
    parser.add_argument("--serial-port",
            action="store",
            dest="serial_port",
            help="virutal COM port path for serial CAN translator")
    parser.add_argument("--serial-baudrate",
            action="store",
            dest="baudrate",
            help="baudrate for serial-connected CAN translator")
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
    else:
        source_class = UsbVehicleInterface
        source_kwargs = dict(vendor_id=arguments.usb_vendor, product_id=arguments.usb_product)

    return source_class, source_kwargs
