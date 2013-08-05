from nose.tools import eq_, ok_
import unittest
import time

from openxc.sources import DataSource
from openxc.measurements import Measurement, NamedMeasurement, \
        UnrecognizedMeasurementError
from openxc.vehicle import Vehicle


class VehicleTests(unittest.TestCase):
    def setUp(self):
        super(VehicleTests, self).setUp()
        self.vehicle = Vehicle()
        self.messages_received = []

    def _callback(self, message):
        self.messages_received.append(message)

    def test_get(self):
        measurement = self.vehicle.get(TestMeasurement)
        ok_(measurement is None)

    def test_add_listener(self):
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._callback)
        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        ok_(len(self.messages_received) > 0)

    def test_remove_listener(self):
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._callback)
        self.vehicle.unlisten(TestMeasurement, self._callback)
        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        eq_(len(self.messages_received), 0)

    def test_get_one(self):
        source = TestDataSource()
        self.vehicle.add_source(source)
        measurement = self.vehicle.get(TestMeasurement)
        ok_(measurement is None)

        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        measurement = self.vehicle.get(TestMeasurement)
        ok_(measurement is not None)
        eq_(measurement.name, data['name'])
        eq_(measurement.value.num, data['value'])

    def test_bad_measurement_type(self):
        class NotAMeasurement(object):
            pass

        try:
            self.vehicle.get(NotAMeasurement)
        except UnrecognizedMeasurementError:
            pass
        else:
            self.fail("Expected an %s" %
                    str(UnrecognizedMeasurementError.__name__))


class TestMeasurement(NamedMeasurement):
    name = "test"


class TestDataSource(DataSource):
    def inject(self, message):
        self.callback(message)
        time.sleep(0.001)

    def run(self):
        pass
