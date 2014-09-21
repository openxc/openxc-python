import unittest

from .streamer_test_utils import BaseStreamerTests, BaseFormatterTests
from openxc.formats.binary import BinaryStreamer, BinaryFormatter

class BinaryStreamerTests(unittest.TestCase, BaseStreamerTests):
    def setUp(self):
        super(BinaryStreamerTests, self).setUp()
        self.streamer = BinaryStreamer()


class BinaryFormatterTests(unittest.TestCase, BaseFormatterTests):
    def setUp(self):
        super(BinaryFormatterTests, self).setUp()
        self.formatter = BinaryFormatter
