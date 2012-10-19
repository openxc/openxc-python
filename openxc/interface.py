from .sources import UsbDataSource, SerialDataSource
from .controllers import UsbControllerMixin, SerialControllerMixin

class UsbVehicleInterface(UsbDataSource, UsbControllerMixin):
    pass

class SerialVehicleInterface(SerialDataSource, SerialControllerMixin):
    pass
