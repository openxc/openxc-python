"""A USB vehicle interface data source."""


import logging
import usb.core
import usb.util

from .base import BytestreamDataSource, DataSourceError

LOG = logging.getLogger(__name__)


class UsbDataSource(BytestreamDataSource):
    """A source to receive data from an OpenXC vehicle interface via USB."""
    DEFAULT_VENDOR_ID = 0x1bc4
    DEFAULT_PRODUCT_ID = 0x0001
    DEFAULT_READ_REQUEST_SIZE = 512

    # If we don't get DEFAULT_READ_REQUEST_SIZE bytes within this number of
    # milliseconds, bail early and return whatever we have - could be zero,
    # could be just less than 512. If data is really pumpin' we can get better
    # throughput if the READ_REQUEST_SIZE is higher, but this delay has to be
    # low enough that a single request isn't held back too long.
    DEFAULT_READ_TIMEOUT = 200

    DEFAULT_INTERFACE_NUMBER = 0
    VEHICLE_DATA_IN_ENDPOINT = 2
    LOG_IN_ENDPOINT = 11

    def __init__(self, vendor_id=None, product_id=None, **kwargs):
        """Initialize a connection to the USB device's IN endpoint.

        Kwargs:
            vendor_id (str or int) - optionally override the USB device vendor
                ID we will attempt to connect to, if not using the OpenXC
                hardware.

            product_id (str or int) - optionally override the USB device product
                ID we will attempt to connect to, if not using the OpenXC
                hardware.

            log_mode - optionally record or print logs from the USB device, which
                are on a separate channel.

        Raises:
            DataSourceError if the USB device with the given vendor ID is not
            connected.
        """
        super(UsbDataSource, self).__init__(**kwargs)
        if vendor_id is not None and not isinstance(vendor_id, int):
            vendor_id = int(vendor_id, 0)
        self.vendor_id = vendor_id or self.DEFAULT_VENDOR_ID

        if product_id is not None and not isinstance(product_id, int):
            product_id = int(product_id, 0)
        self.product_id = product_id or self.DEFAULT_PRODUCT_ID

        devices = usb.core.find(find_all=True, idVendor=self.vendor_id,
                idProduct=self.product_id)
        for device in devices:
            self.device = device
            try:
                self.device.set_configuration()
            except usb.core.USBError as e:
                LOG.warn("Skipping USB device: %s", e)
            else:
                return

        raise DataSourceError("No USB vehicle interface detected - is one plugged in?")

    def read(self, timeout=None):
        return self._read(self.VEHICLE_DATA_IN_ENDPOINT, timeout)

    def read_logs(self, timeout=None):
        return self._read(self.LOG_IN_ENDPOINT, timeout, 64)

    def stop(self):
        super(UsbDataSource, self).stop()
        usb.util.dispose_resources(self.device)

    def _read(self, endpoint_address, timeout=None,
            read_size=DEFAULT_READ_REQUEST_SIZE):
        timeout = timeout or self.DEFAULT_READ_TIMEOUT
        try:
            str(return self.device.read(0x80 + endpoint_address,
                    read_size, self.DEFAULT_INTERFACE_NUMBER, timeout
                    ),'utf-8')
        except (usb.core.USBError, AttributeError) as e:
            if e.errno == 110:
                # Timeout, it may just not be sending
                return ""
            raise DataSourceError("USB device couldn't be read", e)
