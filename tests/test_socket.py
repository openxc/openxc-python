from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources import SocketDataSource
from openxc.sources import DataSourceError

class SocketDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(SocketDataSourceTests, self).setUp()

    def test_create(self):
        def callback(message):
            pass

        try:
            s = SocketDataSource(callback)
        except DataSourceError as e:
            pass
