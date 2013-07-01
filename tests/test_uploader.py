
"""
@file    openxc-python\tests\test_uploader.py OpenXC Test Uploader Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test Uploader Script."""

import unittest

from openxc.sinks import UploaderSink

class UploaderSinkTest(unittest.TestCase):
    """Uploader Sink TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def test_create(self):
        """Test Create Routine"""
        UploaderSink("http://openxcplatform.com")
