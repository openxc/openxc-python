"""Combinations of DataSource with Controller types for duplex vehicle
interfaces."""
from .sources import UsbDataSource, SerialDataSource, NetworkDataSource
from .controllers import UsbControllerMixin, SerialControllerMixin, \
        NetworkControllerMixin

class UsbVehicleInterface(UsbDataSource, UsbControllerMixin):
    """This class is compatibile with an OpenXC CAN translator vehicle interface
    attached via USB. It supports full duplex reads and writes.
    """
    pass

class SerialVehicleInterface(SerialDataSource, SerialControllerMixin):
    """This class is compatibile with an OpenXC CAN translator vehicle interface
    connected via a virtual serial port (e.g. FTDI or Bluetooth). It has full
    read support and limited write support (no control commands are supported).
    """
    pass

class NetworkVehicleInterface(NetworkDataSource, NetworkControllerMixin):
    """This class is compatibile with an OpenXC CAN translator vehicle interface
    connected via the network (e.g. Ethernet or Wi-Fi). It has full
    read support and limited write support (no control commands are supported).
    """
    pass
