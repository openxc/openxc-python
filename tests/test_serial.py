from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources.serial import SerialDataSource
from openxc.sources.base import DataSourceError

class SerialDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(SerialDataSourceTests, self).setUp()

    def test_create(self):
        def callback(message):
            pass

        try:
            s = SerialDataSource(callback)
        except DataSourceError as e:
            pass
