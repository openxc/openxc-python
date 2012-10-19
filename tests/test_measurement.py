from nose.tools import eq_, ok_
import unittest
import time

from openxc.measurements import Measurement, VehicleSpeed

class MeasurementTests(unittest.TestCase):
    def setUp(self):
        super(MeasurementTests, self).setUp()

    def test_basic(self):
        Measurement("name", "value", override_unit=True)

    def test_has_age(self):
        measurement = Measurement("name", "value", override_unit=True)
        age = measurement.age
        time.sleep(0.01)
        ok_(measurement.age > age)

    def test_unit(self):
        measurement = VehicleSpeed(42, override_unit=True)
        try:
            eq_(measurement.value, 42)
        except AttributeError:
            pass
        else:
            self.fail()
        eq_(measurement.value, measurement.unit(42))

    def test_override_unit(self):
        try:
            VehicleSpeed(42)
        except AttributeError:
            pass
        else:
            self.fail()

        VehicleSpeed(42, override_unit=True)

    def test_assign_value(self):
        measurement = VehicleSpeed(42, override_unit=True)
        new_value = VehicleSpeed.unit(42)

        try:
            measurement.value = 24
        except AttributeError:
            eq_(measurement.value, new_value)
        else:
            self.fail()

        measurement.value = new_value
        eq_(measurement.value, new_value)
