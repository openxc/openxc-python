import unittest

from openxc.sinks import FileRecorderSink

class FileRecorderSinkTest(unittest.TestCase):

    def test_create(self):
        FileRecorderSink()
