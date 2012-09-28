from nose.tools import eq_, ok_
import unittest

from openxc.measurements import Measurement
from openxc.vehicle import Vehicle

class VehicleTests(unittest.TestCase):
    def setUp(self):
        super(VehicleTests, self).setUp()
        self.vehicle = Vehicle()

    def test_get(self):
        m = self.vehicle.get(Measurement)
        ok_(m is None)

    def test_add_listener(self):
        def listener():
            pass

        self.vehicle.listen(Measurement, listener)
