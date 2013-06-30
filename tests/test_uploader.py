import unittest

from openxc.sinks import UploaderSink

class UploaderSinkTest(unittest.TestCase):
    """Uploader Sink TestCase Class"""
    def test_create(self):
        """Test Create Routine"""
        UploaderSink("http://openxcplatform.com")
