from nose.tools import eq_, ok_
import unittest

from openxc.measurements import Measurement, VehicleSpeed

class MeasurementTests(unittest.TestCase):
    def setUp(self):
        super(MeasurementTests, self).setUp()

    def test_basic(self):
        Measurement("name", "value")

    def test_has_age(self):
        measurement = Measurement("name", "value")
        age = measurement.age
        ok_(measurement.age > age)

    def test_unit(self):
        measurement = VehicleSpeed(42)
        try:
            eq_(measurement.value, 42)
        except AttributeError:
            pass
        else:
            self.fail()
        eq_(measurement.value, measurement.unit(42))
