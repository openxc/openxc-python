from nose.tools import eq_, ok_
import unittest

import openxc.measurements
from openxc.measurements import Measurement

class MeasurementTests(unittest.TestCase):
    def setUp(self):
        super(MeasurementTests, self).setUp()

    def test_basic(self):
        measurement = Measurement("name", "value")

    def test_has_age(self):
        measurement = Measurement("name", "value")
        age = measurement.age
        ok_(measurement.age > age)
