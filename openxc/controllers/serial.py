from __future__ import absolute_import

import logging

from .base import Controller

LOG = logging.getLogger(__name__)


class SerialControllerMixin(Controller):
    def write_bytes(self, data):
        return self.device.write(data)
