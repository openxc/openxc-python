import unittest

from .streamer_test_utils import BaseStreamerTests, BaseFormatterTests
from openxc.formats.json import JsonStreamer, JsonFormatter

class JsonStreamerTests(unittest.TestCase, BaseStreamerTests):
    def setUp(self):
        super(JsonStreamerTests, self).setUp()
        self.streamer = JsonStreamer()

class JsonFormatterTests(unittest.TestCase, BaseFormatterTests):
    def setUp(self):
        super(JsonFormatterTests, self).setUp()
        self.formatter = JsonFormatter
