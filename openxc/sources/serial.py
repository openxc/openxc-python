"""A virtual serial port data source."""
from __future__ import absolute_import

import logging

from .base import BytestreamDataSource, DataSourceError

LOG = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    LOG.debug("serial library not installed, can't use serial interface")


class SerialDataSource(BytestreamDataSource):
    """A data source reading from a serial port, which could be implemented
    with a USB to Serial or Bluetooth adapter.
    """
    DEFAULT_PORT = "/dev/ttyUSB0"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, callback=None, port=None, baudrate=None):
        """Initialize a connection to the serial device.

        Kwargs:
            port - optionally override the default virtual COM port
            baudrate - optionally override the default baudrate

        Raises:
            DataSourceError if the serial device cannot be opened.
        """
        super(SerialDataSource, self).__init__(callback)
        port = port or self.DEFAULT_PORT
        baudrate = baudrate or self.DEFAULT_BAUDRATE
        try:
            self.device = serial.Serial(port, baudrate, rtscts=True)
        except serial.SerialException as e:
            raise DataSourceError("Unable to open serial device at port "
                    "%s: %s" % (port, e))
        else:
            LOG.debug("Opened serial device at %s", port)

    def _read(self):
        return self.device.readline()
