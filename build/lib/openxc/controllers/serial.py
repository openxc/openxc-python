"""Controller implementation for a virtual serial device."""
from __future__ import absolute_import

from .base import Controller


class SerialControllerMixin(Controller):
    """An implementation of a Controller type that connects to a virtual serial
    device.

    This class acts as a mixin, and expects ``self.device`` to be an instance
    of ``serial.Serial``.

    TODO bah, this is kind of weird. refactor the relatinoship between
    sources/controllers.
    """
    def write_bytes(self, data):
        return self.device.write(data)
