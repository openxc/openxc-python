import argparse

def device_options():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--usb-vendor",
            action="store",
            dest="usb_vendor")
    parser.add_argument("--serial", "-s",
            action="store_true",
            dest="serial",
            default=False)
    parser.add_argument("--serial-port",
            action="store",
            dest="serial_port")
    parser.add_argument("--serial-baudrate",
            action="store",
            dest="baudrate")
    return parser
