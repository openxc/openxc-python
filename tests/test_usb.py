from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.sources.usb import UsbDataSource
from openxc.sources.base import DataSourceError

class UsbDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(UsbDataSourceTests, self).setUp()

    def test_create(self):
        def callback(message):
            pass

        try:
            s = UsbDataSource(callback)
        except DataSourceError as e:
            pass
