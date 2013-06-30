from nose.tools import eq_, ok_
import unittest
import time

from openxc.measurements import Measurement, VehicleSpeed

class MeasurementTests(unittest.TestCase):
    """Measurement Tests TestCase Class"""
    def setUp(self):
        """Setup Routine"""
        super(MeasurementTests, self).setUp()

    def test_basic(self):
        """Test Basic Routine"""
        Measurement("name", "value", override_unit=True)

    def test_has_age(self):
        """Test Has Age Routine"""
        measurement = Measurement("name", "value", override_unit=True)
        age = measurement.age
        time.sleep(0.001)
        ok_(measurement.age > age)

    def test_unit(self):
        """Test Unit Routine"""
        measurement = VehicleSpeed(42, override_unit=True)
        try:
            eq_(measurement.value, 42)
        except AttributeError:
            pass
        else:
            self.fail()
        eq_(measurement.value, measurement.unit(42))

    def test_override_unit(self):
        """Override Unit Test Routine"""
        try:
            VehicleSpeed(42)
        except AttributeError:
            pass
        else:
            self.fail()

        VehicleSpeed(42, override_unit=True)

    def test_assign_value(self):
        """Assign Value Test Routine"""
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
