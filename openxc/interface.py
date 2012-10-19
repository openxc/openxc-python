from .sources.usb import UsbDataSource
from .sources.serial import SerialDataSource
from .controllers.usb import UsbControllerMixin
from .controllers.serial import SerialControllerMixin

class UsbVehicleInterface(UsbDataSource, UsbControllerMixin):
    pass

class SerialVehicleInterface(SerialDataSource, SerialControllerMixin):
    pass
