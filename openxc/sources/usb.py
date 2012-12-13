"""A USB vehicle interface data source."""
from __future__ import absolute_import

import logging
import usb.core

from .base import BytestreamDataSource, DataSourceError

LOG = logging.getLogger(__name__)


class UsbDataSource(BytestreamDataSource):
    """A source to receive data from an OpenXC vehicle interface via USB."""
    DEFAULT_VENDOR_ID = 0x1bc4
    DEFAULT_PRODUCT_ID = 0x0001
    DEFAULT_READ_REQUEST_SIZE = 512
    DEFAULT_READ_TIMEOUT = 1000000

    VERSION_CONTROL_COMMAND = 0x80
    RESET_CONTROL_COMMAND = 0x81

    def __init__(self, callback=None, vendor_id=None, product_id=None):
        """Initialize a connection to the USB device's IN endpoint.

        Kwargs:
            vendor_id (str or int) - optionally override the USB device vendor
                ID we will attempt to connect to, if not using the OpenXC
                hardware.

            product_id (str or int) - optionally override the USB device product
                ID we will attempt to connect to, if not using the OpenXC
                hardware.

        Raises:
            DataSourceError if the USB device with the given vendor ID is not
            connected.
        """
        super(UsbDataSource, self).__init__(callback)
        if vendor_id is not None and not isinstance(vendor_id, int):
            vendor_id = int(vendor_id, 0)
        self.vendor_id = vendor_id or self.DEFAULT_VENDOR_ID

        if product_id is not None and not isinstance(product_id, int):
            product_id = int(product_id, 0)
        self.product_id = product_id or self.DEFAULT_PRODUCT_ID

        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        self.in_endpoint = None

        if not self.device:
            raise DataSourceError("Couldn't find a USB product 0x%x from vendor 0x%x"
                    % (self.product_id, self.vendor_id))
        self.device.set_configuration()
        self.in_endpoint = self._connect_in_endpoint(self.device)

    def _read(self, timeout=None):
        timeout = timeout or self.DEFAULT_READ_TIMEOUT
        if self.in_endpoint is None:
            LOG.warn("Can't read from USB, IN endpoint is %s", self.in_endpoint)
            return ""
        else:
            return self.in_endpoint.read(self.DEFAULT_READ_REQUEST_SIZE,
                    timeout).tostring()

    @staticmethod
    def _connect_in_endpoint(device):
        """Open a reference to the USB device's only IN endpoint. This method
        assumes that the USB device configuration has already been set.
        """
        config = device.get_active_configuration()
        interface_number = config[(0, 0)].bInterfaceNumber
        interface = usb.util.find_descriptor(config,
                bInterfaceNumber=interface_number)

        in_endpoint = usb.util.find_descriptor(interface,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_IN)

        if not in_endpoint:
            raise DataSourceError("Couldn't find IN endpoint on the USB device")
        return in_endpoint

