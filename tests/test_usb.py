import unittest

from openxc.sources import UsbDataSource, DataSourceError

class UsbDataSourceTests(unittest.TestCase):
    """USB Data Source Tests TestCase Class"""
    def setUp(self):
        """Setup Routine"""
        super(UsbDataSourceTests, self).setUp()

    def test_create(self):
        """Test Create Routine"""
        def callback(message):
            pass
