"""Controller implementation for a virtual serial device."""
from __future__ import absolute_import
import time

from .base import Controller


class SerialControllerMixin(Controller):
    """An implementation of a Controller type that connects to a virtual serial
    device.

    This class acts as a mixin, and expects ``self.device`` to be an instance
    of ``serial.Serial``.

    TODO Bah, this is kind of weird. refactor the relationship between
    sources/controllers.
    """

    WAITIED_FOR_CONNECTION = False

    def write_bytes(self, data):
        return self.device.write(data)

    def complex_request(self, request, blocking=True):
        if not self.WAITIED_FOR_CONNECTION:
            # TODO need to wait until device is connected or errors out
            # that may be a bug in the bluetooth stack, see
            # https://bugzilla.redhat.com/show_bug.cgi?id=1060457
            time.sleep(5)
        return super(SerialControllerMixin, self).complex_request(request, blocking)
