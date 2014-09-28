import unittest

from .streamer_test_utils import BaseStreamerTests, BaseFormatterTests
from openxc.formats.binary import ProtobufStreamer, ProtobufFormatter

class ProtobufStreamerTests(unittest.TestCase, BaseStreamerTests):
    def setUp(self):
        super(ProtobufStreamerTests, self).setUp()
        self.streamer = ProtobufStreamer()


class ProtobufFormatterTests(unittest.TestCase, BaseFormatterTests):
    def setUp(self):
        super(ProtobufFormatterTests, self).setUp()
        self.formatter = ProtobufFormatter
