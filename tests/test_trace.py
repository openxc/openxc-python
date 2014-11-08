import unittest
from nose.tools import ok_

from openxc.sources import TraceDataSource

class TraceDataSourceTests(unittest.TestCase):
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
