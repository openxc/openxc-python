import unittest
from nose.tools import ok_

from openxc.sources import TraceDataSource

class TraceDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(TraceDataSourceTests, self).setUp()
        self.source = TraceDataSource(filename="/tmp/not-a-file")

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

