"""Controller implementation for a network device."""
from __future__ import absolute_import

from .base import Controller


class NetworkControllerMixin(Controller):
    """An implementation of a Controller type that connects to a networked
    device.

    This class acts as a mixin, and expects ``self.stream`` to be an instance
    of a file object, connected to a socket.

    """
    def write_bytes(self, data):
        return self.stream.write(data)
