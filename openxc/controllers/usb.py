"""Controller implementation for an OpenXC USB device."""


import logging
import usb.core

from .base import Controller, ControllerError

LOG = logging.getLogger(__name__)


class UsbControllerMixin(Controller):
    """An implementation of a Controller type that connects to an OpenXC USB
    device.

    This class acts as a mixin, and expects ``self.device`` to be an instance
    of ``usb.Device``.

    TODO bah, this is kind of weird. refactor the relationship between
    sources/controllers.
    """
    COMPLEX_CONTROL_COMMAND = 0x83

    def write_bytes(self, data):
        if self.out_endpoint is None:
            LOG.warn("Can't write \"%s\" to USB, OUT endpoint is %x", data,
                    self.out_endpoint)
            return 0
        else:
            return self.out_endpoint.write(data)

    def _send_complex_request(self, request):
        """Send a request via the USB control request endpoint, rather than as a
        bulk transfer.
        """
        # LOG.warn("DEBUG STUFF ________________ " + str(self.streamer.serialize_for_stream(request)))
        self.device.ctrl_transfer(0x40, self.COMPLEX_CONTROL_COMMAND, 0, 0,
                self.streamer.serialize_for_stream(request))

    @property
    def out_endpoint(self):
        """Open a reference to the USB device's only OUT endpoint. This method
        assumes that the USB device configuration has already been set.
        """
        if getattr(self, '_out_endpoint', None) is None:
            config = self.device.get_active_configuration()
            interface_number = config[(0, 0)].bInterfaceNumber
            interface = usb.util.find_descriptor(config,
                    bInterfaceNumber=interface_number)

            self._out_endpoint = usb.util.find_descriptor(interface,
                    custom_match = \
                            lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_OUT)

            if not self._out_endpoint:
                raise ControllerError(
                        "Couldn't find OUT endpoint on the USB device")
        return self._out_endpoint
