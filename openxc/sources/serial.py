
"""
@file    openxc-python\openxc\sources\serial.py Serial Sources Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   A virtual serial port data source."""

from __future__ import absolute_import

import logging

from .base import BytestreamDataSource, DataSourceError

## @var LOG
# The logging object instance.
LOG = logging.getLogger(__name__)

## @var serial
# The serial object instance.

try:
    import serial
except ImportError:
    LOG.debug("serial library not installed, can't use serial interface")
    serial = None


class SerialDataSource(BytestreamDataSource):
    """A data source reading from a serial port, which could be implemented
    with a USB to Serial or Bluetooth adapter.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var DEFAULT_PORT
    # The default serial port to read from.
    DEFAULT_PORT = "/dev/ttyUSB0"
    ## @var DEFAULT_BAUDRATE
    # The default serial port baud rate.
    DEFAULT_BAUDRATE = 230400
    
    ## @var device
    # The device object instance.
    
    def __init__(self, callback=None, port=None, baudrate=None):
        """Initialize a connection to the serial device.

        Kwargs:
            port - optionally override the default virtual COM port
            baudrate - optionally override the default baudrate

        Raises:
            DataSourceError if the serial device cannot be opened.
            
        @param callback The callback function name.
        @param port optionally override the default virtual COM port.
        @param baudrate optionally override the default baudrate.
        @exception DataSourceError if the serial device cannot be opened.
        """
        super(SerialDataSource, self).__init__(callback)
        port = port or self.DEFAULT_PORT
        baudrate = baudrate or self.DEFAULT_BAUDRATE

        if serial is None:
            raise DataSourceError("pyserial library is not available")

        try:
            self.device = serial.Serial(port, baudrate, rtscts=True)
        except serial.SerialException as e:
            raise DataSourceError("Unable to open serial device at port "
                    "%s: %s" % (port, e))
        else:
            LOG.debug("Opened serial device at %s", port)

    def _read(self):
        """Read Routine"""
        return self.device.readline()
