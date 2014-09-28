import unittest

from .streamer_test_utils import BaseStreamerTests, BaseFormatterTests
from openxc.formats.binary import ProtobufStreamer, BinaryFormatter

class ProtobufStreamerTests(unittest.TestCase, BaseStreamerTests):
    def setUp(self):
        super(ProtobufStreamerTests, self).setUp()
        self.streamer = ProtobufStreamer()


class BinaryFormatterTests(unittest.TestCase, BaseFormatterTests):
    def setUp(self):
        super(BinaryFormatterTests, self).setUp()
        self.formatter = BinaryFormatter
