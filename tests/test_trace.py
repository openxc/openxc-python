import unittest
from nose.tools import ok_
import time

from openxc.sources import TraceDataSource

class TraceDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(TraceDataSourceTests, self).setUp()
        self.source = TraceDataSource()

    def test_validate(self):
        """
        The validate method if private, but we're going to test it anyway
        since we lack a larger integrate test suite for the TraceDataSource
        class.
        """
        good_message = {'name': "data", 'value': 42}
        bad_message = {'name': "data"}
        ok_(not self.source._validate(bad_message))
        ok_(self.source._validate(good_message))

    def _receive(self, message, **kwargs):
        self.received = True

    def test_without_timestamp(self):
        self.source = TraceDataSource(filename="tests/trace-no-timestamp.json",
                callback=self._receive, loop=False)
        self.received = False
        self.source.start()
        self.source.join()
        ok_(self.received)

    def test_playback(self):
        self.source = TraceDataSource(filename="tests/trace.json",
                callback=self._receive, loop=False)
        self.received = False
        self.source.start()
        self.source.join()
        ok_(self.received)
