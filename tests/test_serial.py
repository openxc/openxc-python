from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources import SerialDataSource
from openxc.sources import DataSourceError

class SerialDataSourceTests(unittest.TestCase):
    """Serial Data Source Tests TestCase Class"""
    def setUp(self):
        """Setup Routine"""
        super(SerialDataSourceTests, self).setUp()

    def test_create(self):
        """Test Create Routine"""
        def callback(message):
            pass

        try:
            s = SerialDataSource(callback)
        except DataSourceError as e:
            pass
