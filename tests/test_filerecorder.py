import unittest

from openxc.sinks import FileRecorderSink

class FileRecorderSinkTest(unittest.TestCase):
    """File Recorder Sink Test TestCase Class"""
    def test_create(self):
        """Create Test Routine"""
        FileRecorderSink()
