import unittest

from openxc.sources import UsbDataSource, DataSourceError

class UsbDataSourceTests(unittest.TestCase):
    def setUp(self):
        super(UsbDataSourceTests, self).setUp()

    def test_create(self):
        def callback(message):
            pass
