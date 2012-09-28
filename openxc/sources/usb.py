from __future__ import absolute_import

import logging
import usb.core

from .base import DataSource

log = logging.getLogger(__name__)

class UsbDataSource(DataSource):
    DEFAULT_VENDOR_ID = 0x1bc4
    VERSION_CONTROL_COMMAND = 0x80
    RESET_CONTROL_COMMAND = 0x81

    DEFAULT_READ_REQUEST_SIZE = 512
    DEFAULT_READ_TIMEOUT = 1000000

    def __init__(self, vendor_id=None):
        super(UsbDataSource, self).__init__()
        self.vendor_id = vendor_id or self.DEFAULT_VENDOR_ID

        self.device = usb.core.find(idVendor=self.vendor_id)

        if not self.device:
            log.warn("Couldn't find a USB device from vendor 0x%x",
                    self.vendor_id)
            return

        self.in_endpoint, self.out_endpoint = self.connect_endpoints(self
                .device)

    def _connect_endpoints(self, device):
        device.set_configuration()
        config = device.get_active_configuration()
        interface_number = config[(0, 0)].bInterfaceNumber
        interface = usb.util.find_descriptor(config,
                bInterfaceNumber=interface_number)

        out_endpoint = usb.util.find_descriptor(interface,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)
        in_endpoint = usb.util.find_descriptor(interface,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_IN)

        if not out_endpoint or not in_endpoint:
            log.warn("Couldn't find proper endpoints on the USB device")

        return out_endpoint, in_endpoint

    def read(self, num_bytes=None, timeout=None):
        num_bytes = num_bytes or self.DEFAULT_READ_REQUEST_SIZE
        timeout = timeout or self.DEFAULT_READ_TIMEOUT
        return self.in_endpoint.read(num_bytes, timeout).tostring()

    def _write(self, message):
        return self.out_endpoint.write(message)

    def version(self):
        raw_version = self.device.ctrl_transfer(0xC0,
                self.VERSION_CONTROL_COMMAND, 0, 0, 100)
        return ''.join([chr(x) for x in raw_version])

    def reset(self):
        self.device.ctrl_transfer(0x40, self.RESET_CONTROL_COMMAND, 0, 0)
