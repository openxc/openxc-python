"""Controller implementation for an OpenXC USB device."""
from __future__ import absolute_import

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

    @property
    def out_endpoint(self):
        if getattr(self, '_out_endpoint', None) is None:
            self._out_endpoint = self._connect_out_endpoint(self.device)
        return self._out_endpoint

    def write_bytes(self, data):
        if self.out_endpoint is None:
            LOG.warn("Can't write \"%s\" to USB, OUT endpoint is %x", data,
                    self.out_endpoint)
            return 0
        else:
            return self.out_endpoint.write(data)

    def version(self):
        raw_version = self.device.ctrl_transfer(0xC0,
                self.VERSION_CONTROL_COMMAND, 0, 0, 100)
        return ''.join([chr(x) for x in raw_version])

    def reset(self):
        self.device.ctrl_transfer(0x40, self.RESET_CONTROL_COMMAND, 0, 0)

    @staticmethod
    def _connect_out_endpoint(device):
        """Open a reference to the USB device's only OUT endpoint. This method
        assumes that the USB device configuration has already been set.
        """
        config = device.get_active_configuration()
        interface_number = config[(0, 0)].bInterfaceNumber
        interface = usb.util.find_descriptor(config,
                bInterfaceNumber=interface_number)

        out_endpoint = usb.util.find_descriptor(interface,
                custom_match = \
                        lambda e: \
                        usb.util.endpoint_direction(e.bEndpointAddress) == \
                        usb.util.ENDPOINT_OUT)

        if not out_endpoint:
            raise ControllerError(
                    "Couldn't find OUT endpoint on the USB device")
        return out_endpoint
