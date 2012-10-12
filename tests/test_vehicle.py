from nose.tools import eq_, ok_
import unittest

from openxc.sources.base import DataSource
from openxc.measurements import Measurement, UnrecognizedMeasurementError
from openxc.vehicle import Vehicle


class VehicleTests(unittest.TestCase):
    def setUp(self):
        super(VehicleTests, self).setUp()
        self.vehicle = Vehicle()
        self.messages_received = []

    def _listener(self, message):
        self.messages_received.append(message)

    def test_get(self):
        measurement = self.vehicle.get(TestMeasurement)
        ok_(measurement is None)

    def test_add_listener(self):
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._listener)
        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        ok_(len(self.messages_received) > 0)

    def test_remove_listener(self):
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._listener)
        self.vehicle.unlisten(TestMeasurement, self._listener)
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
        eq_(measurement.value, data['value'])

    def test_bad_measurement_type(self):
        try:
            self.vehicle.get(Measurement)
        except UnrecognizedMeasurementError:
            pass
        else:
            self.fail("Expected an %s" %
                    str(UnrecognizedMeasurementError.__name__))


class TestMeasurement(Measurement):
    name = "test"


class TestDataSource(DataSource):
    def inject(self, message):
        self.callback(message)

    def run(self):
        pass
