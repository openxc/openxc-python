
"""
@file    openxc-python\tests\test_usb.py OpenXC Test USB Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test USB Script."""

import unittest

from openxc.sources import UsbDataSource, DataSourceError

class UsbDataSourceTests(unittest.TestCase):
    """USB Data Source Tests TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def setUp(self):
        """Setup Routine"""
        super(UsbDataSourceTests, self).setUp()

    def test_create(self):
        """Test Create Routine"""
        def callback(message):
            """Callback Routine"""
            pass
