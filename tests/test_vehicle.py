
"""
@file    openxc-python\tests\test_vehicle.py OpenXC Test Vehicle Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test Vehicle Script."""

from nose.tools import eq_, ok_
import unittest
import time

from openxc.sources import DataSource
from openxc.measurements import Measurement, NamedMeasurement, \
        UnrecognizedMeasurementError
from openxc.vehicle import Vehicle

class VehicleTests(unittest.TestCase):
    """Vehicle Tests TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var vehicle
    # The vehicle object instance.
    ## @var messages_received
    # The messages received instance.
    
    def setUp(self):
        """Set up Routine"""
        super(VehicleTests, self).setUp()
        self.vehicle = Vehicle()
        self.messages_received = []

    def _callback(self, message):
        """Callback Routine"""
        self.messages_received.append(message)

    def test_get(self):
        """Test Get Routine"""
        measurement = self.vehicle.get(TestMeasurement)
        ok_(measurement is None)

    def test_add_listener(self):
        """Test Add Listener"""
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._callback)
        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        ok_(len(self.messages_received) > 0)

    def test_remove_listener(self):
        """Test Remove Listener"""
        source = TestDataSource()
        self.vehicle.add_source(source)

        self.vehicle.listen(TestMeasurement, self._callback)
        self.vehicle.unlisten(TestMeasurement, self._callback)
        data = {'name': TestMeasurement.name, 'value': 100}
        source.inject(data)
        eq_(len(self.messages_received), 0)

    def test_get_one(self):
        """Test Get One Routine"""
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
        """Test Bad Measurement Type Routine"""
        try:
            self.vehicle.get(Measurement)
        except UnrecognizedMeasurementError:
            pass
        else:
            self.fail("Expected an %s" %
                    str(UnrecognizedMeasurementError.__name__))


class TestMeasurement(NamedMeasurement):
    """Test Measurement
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name of this Measurement instance.
    name = "test"


class TestDataSource(DataSource):
    """Test Data Source Class"""
    def inject(self, message):
        """Inject Routine
        @param message The message to send to the callback routine."""
        self.callback(message)
        time.sleep(0.001)

    def run(self):
        """The Run Routine"""
        pass
