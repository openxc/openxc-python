
"""
@file    openxc-python\openxc\interface.py OpenXC Interface Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Combinations of DataSource with Controller types for duplex vehicle 
         interfaces."""

from .sources import UsbDataSource, SerialDataSource
from .controllers import UsbControllerMixin, SerialControllerMixin

class UsbVehicleInterface(UsbDataSource, UsbControllerMixin):
    """This class is compatibile with an OpenXC CAN translator vehicle interface
    attached via USB. It supports full duplex reads and writes.
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    pass

class SerialVehicleInterface(SerialDataSource, SerialControllerMixin):
    """This class is compatibile with an OpenXC CAN translator vehicle interface
    connected via a virtual serial port (e.g. FTDI or Bluetooth). It has full
    read support and limited write support (no control commands are supported).
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    pass
