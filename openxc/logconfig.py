
"""
@file    openxc-python\openxc\logconfig.py OpenXC Log Configuration Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Log Configuration Script."""

import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Null Handler Class"""
        def emit(self, record):
            """Emit Routine"""
            pass

logging.getLogger("openxc").addHandler(NullHandler())
