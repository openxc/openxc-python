from __future__ import absolute_import

import logging
import serial

from .base import DataSource

log = logging.getLogger(__name__)

class SerialDataSource(DataSource):
    DEFAULT_PORT = "/dev/ttyUSB0"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, callback, port=None, baudrate=None):
        super(SerialDataSource, self).__init__(callback)
        self.port = port or self.DEFAULT_PORT
        self.baudrate = baudrate or self.DEFAULT_BAUDRATE
        try:
            self.device = serial.Serial(self.port, self.baudrate)
        except serial.SerialException as e:
            log.warn("Unable to open serial device", e)
            self.device = None
        else:
            log.debug("Opened serial device at %s", self.port)

    def read(self):
        if self.device:
            return self.device.readline()
        return ""

    def _write(self, message):
        if self.device:
            return self.device.write(message )
