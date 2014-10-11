from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources import NetworkDataSource
from openxc.sources import DataSourceError

class NetworkDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(NetworkDataSourceTests, self).setUp()

    def test_create(self):
        def callback(message):
            pass

        try:
            s = NetworkDataSource(callback=callback, host='localhost')
        except DataSourceError as e:
            pass
