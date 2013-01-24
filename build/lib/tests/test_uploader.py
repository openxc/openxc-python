import unittest

from openxc.sinks import UploaderSink

class UploaderSinkTest(unittest.TestCase):

    def test_create(self):
        UploaderSink("http://openxcplatform.com")
