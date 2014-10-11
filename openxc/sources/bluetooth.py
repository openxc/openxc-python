"""A Bluetooth data source."""
from __future__ import absolute_import

import logging

from .socket import SocketDataSource
from .base import DataSourceError

LOG = logging.getLogger(__name__)

try:
    import bluetooth
except ImportError:
    LOG.debug("pybluez library not installed, can't use bluetooth interface")
    bluetooth = None


class BluetoothVehicleInterface(SocketDataSource):
    """A data source reading from a bluetooth device.
    """

    OPENXC_DEVICE_NAME_PREFIX = "OpenXC-VI-"

    def __init__(self, address=None, **kwargs):
        """Initialize a connection to the bluetooth device.

        Raises:
            DataSourceError if the bluetooth device cannot be opened.
        """
        super(BluetoothVehicleInterface, self).__init__(**kwargs)
        self.address = address

        if bluetooth is None:
            raise DataSourceError("pybluez library is not available")

        while self.address is None:
            self.scan_for_bluetooth_device()
        self.connect()

    def connect(self):
        # TODO push this to a background connecting thread so the constructor
        # can return
        port = 1
        connected = False
        while not connected:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            try:
                self.socket.connect((self.address, port))
            except IOError as e:
                LOG.warn("Unable to connect to %s" % self.address, e)
            else:
                LOG.info("Opened bluetooth device at %s", port)
                connected = True

    def scan_for_bluetooth_device(self):
        nearby_devices = bluetooth.discover_devices()

        self.address = None
        device_name = None
        for address in nearby_devices:
            device_name = bluetooth.lookup_name(address)
            if device_name.startswith(self.OPENXC_DEVICE_NAME_PREFIX):
                self.address = address
                break

        if self.address is not None:
            LOG.info("Discovered OpenXC VI %s (%s)" % (device_name, self.address))
        else:
            LOG.info("No OpenXC VI devices discovered")
