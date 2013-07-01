
"""
@file    openxc-python\openxc\controllers\serial.py Serial Controller Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Controller implementation for a virtual serial device.
"""

from __future__ import absolute_import

from .base import Controller


class SerialControllerMixin(Controller):
    """An implementation of a Controller type that connects to a virtual serial
    device.

    This class acts as a mixin, and expects ``self.device`` to be an instance
    of ``serial.Serial``.

    TODO bah, this is kind of weird. refactor the relatinoship between
    sources/controllers.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def write_bytes(self, data):
        """Write Bytes Routine"""
        return self.device.write(data)
