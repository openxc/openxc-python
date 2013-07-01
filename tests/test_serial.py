
"""
@file    openxc-python\tests\test_serial.py OpenXC Test Serial Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test Serial Script."""

from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources import SerialDataSource
from openxc.sources import DataSourceError

class SerialDataSourceTests(unittest.TestCase):
    """Serial Data Source Tests TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def setUp(self):
        """Setup Routine"""
        super(SerialDataSourceTests, self).setUp()

    def test_create(self):
        """Test Create Routine"""
        def callback(message):
            pass

        try:
            s = SerialDataSource(callback)
        except DataSourceError as e:
            pass
