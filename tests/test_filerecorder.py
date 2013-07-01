
"""
@file    openxc-python\tests\test_filerecorder.py OpenXC Test File Recorder 
         Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test File Recorder Script."""

import unittest

from openxc.sinks import FileRecorderSink

class FileRecorderSinkTest(unittest.TestCase):
    """File Recorder Sink Test TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def test_create(self):
        """Create Test Routine"""
        FileRecorderSink()
