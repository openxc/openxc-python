from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources.serial import SerialDataSource

class SerialDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(SerialDataSourceTests, self).setUp()

    def test_create(self):
        s = SerialDataSource()
