from __future__ import absolute_import

import logging
import serial

from .base import DataSource, DataSourceError

LOG = logging.getLogger(__name__)

class SerialDataSource(DataSource):
    DEFAULT_PORT = "/dev/ttyUSB0"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, callback=None, port=None, baudrate=None):
        super(SerialDataSource, self).__init__(callback)
        port = port or self.DEFAULT_PORT
        baudrate = baudrate or self.DEFAULT_BAUDRATE
        try:
            self.device = serial.Serial(port, baudrate)
        except serial.SerialException as e:
            raise DataSourceError("Unable to open serial device at port "
                    "%s: %s" % (port, e))
        else:
            LOG.debug("Opened serial device at %s", port)

    def read(self):
        return self.device.readline()

    def _write(self, message):
        return self.device.write(message )
