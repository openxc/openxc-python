
"""
@file    openxc-python\openxc\measurements.py OpenXC Measurements Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   Vehicle data measurement types pre-defined in OpenXC."""
import numbers

import openxc.units as units
from .utils import Range, AgingData

try:
    unicode
except NameError:
    ## @var basestring
    # Definition for Python 3
    basestring = unicode = str

class Measurement(AgingData):
    """Measurement Class
    
    @brief The Measurement is the base type of all values read from an OpenXC
    vehicle interface. All values encapsulated in a Measurement have an
    associated scalar unit (e.g. meters, degrees, etc) to avoid crashing a rover
    into Mars.
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var DATA_TYPE
    # The data type object instance.
    DATA_TYPE = numbers.Number
    ## @var _measurement_map
    # The measurement map dictionary for this object instance.
    _measurement_map = {}
    ## @var unit
    # The unit object instance.
    unit = units.Undefined
    
    ## @var name
    # The name object instance.
    ## @var value
    # The value instance.
    ## @var event
    # The event for the compound Measurements.
    
    def __init__(self, name, value, event=None, override_unit=False, **kwargs):
        """Construct a new Measurement with the given name and value.
        
        Args:
            name (str):  The Measurement's generic name in OpenXC.
            value (str, float, or bool): The Measurement's value.

        Kwargs:
           event (str, bool): An optional event for compound Measurements.
           override_unit (bool): The value will be coerced to the correct units
               if it is a plain number.

        Raises:
            UnrecognizedMeasurementError if the value is not the correct units,
            e.g. if it's a string and we're expecting a numerical value
        
        @author  Christopher Peplin github@rhubarbtech.com
        @date    June 25, 2013
        @version 0.9.4
        
        @param name The name of the measurement
        @param value The value of the measurement
        @param event (str, bool): An optional event for compound Measurements.
        @param override_unit The override unit
        @param kwargs The kwargs instance.
        @exception UnrecognizedMeasurementError if the value is not the correct
        units, e.g. if it's a string and we're expecting a numerical value.
        """
        super(Measurement, self).__init__()
        self.name = name
        if self.unit != units.Undefined and override_unit:
            if type(value) == unicode:
                raise UnrecognizedMeasurementError("%s value cannot be a string"
                        % self.__class__)
            value = self.unit(value)
        self.value = value
        self.event = event

    def __repr__(self):
        """String Representation"""
        return str(self.value)

    @property
    def value(self):
        """Value Property"""
        return self._value

    @value.setter
    def value(self, new_value):
        """Set the value of this measurement.

        Raises:
            AttributeError: if the new value isn't of the correct units.
        
        @param new_value The new value for this measurement instance.
        @exception AttributeError if the new value isn't of the correct units.
        """
        if self.unit != units.Undefined and new_value.unit != self.unit:
            raise AttributeError("%s must be in %s" % (
                self.__class__, self.unit))
        self._value = new_value

    @classmethod
    def from_dict(cls, data):
        """Create a new Measurement subclass instance using the given dict.

        If Measurement.name_from_class was previously called with this data's
        associated Measurement sub-class in Python, the returned object will be
        an instance of that sub-class. If the measurement name in ``data`` is
        unrecognized, the returned object will be of the generic ``Measurement``
        type.

        Args:
            data (dict): the data for the new measurement, including at least a
                name and value.
        
        @param cls the object instance.
        @param data the data object instance.
        """
        measurement_class = cls._class_from_name(data['name'])
        args = [data['value']]
        if measurement_class == Measurement:
            args.insert(0, data['name'])
        return measurement_class(*args, event=data.get('event', None),
                override_unit=True)

    @classmethod
    def name_from_class(cls, measurement_class):
        """For a given measurement class, return its generic name.

        The given class is expected to have a ``name`` attribute, otherwise this
        function will raise an execption. The point of using this method instead
        of just trying to grab that attribute in the application is to cache
        measurement name to class mappings for future use.

        Returns:
            the generic OpenXC name for a measurement class.

        Raise:
            UnrecognizedMeasurementError: if the class does not have a valid
                generic name
        
        @param cls the object instance.
        @param measurement_class the measurement class object instance.
        """
        try:
            name = getattr(measurement_class, 'name')
        except AttributeError:
            raise UnrecognizedMeasurementError()
        else:
            cls._measurement_map[name] = measurement_class
            return name

    @classmethod
    def _class_from_name(cls, measurement_name):
        """Class From Name
        Wparam cls The object instance.
        @param measurement_name Contains the measurement name for this 
        instance."""
        return cls._measurement_map.get(measurement_name, Measurement)


class NamedMeasurement(Measurement):
    """A NamedMeasurement has a class-level ``name`` variable and thus the
    ``name`` argument is not required in its constructor.
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def __init__(self, value, **kwargs):
        """Initialization Routine
        @param value The named measurement value.
        @param kwargs Additional input."""
        super(NamedMeasurement, self).__init__(self.name, value, **kwargs)


class NumericMeasurement(NamedMeasurement):
    """A NumericMeasurement must have a numeric value and thus a valid range of
    acceptable values.
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var valid_range
    # The valid range object instance.
    valid_range = None

    def within_range(self):
        """Within Range Routine"""
        return self.valid_range.within_range(self.value.num)


class StatefulMeasurement(NamedMeasurement):
    """Stateful Measurement Class
    
    @brief Must have a class-level ``states`` member that defines a set of  
    valid string states for this measurement's value.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var DATA_TYPE
    # The data type object instance.
    DATA_TYPE = unicode
    ## @var states
    # The current state of this StatefulMeasurement instance.
    states = None
    
    def valid_state(self):
        """Determine if the current state is valid, given the class' ``state``
        member.

        Returns:
            True if the value is a valid state.
        """
        return self.states is not None and self.value in self.states


class BooleanMeasurement(NamedMeasurement):
    """Boolean Measurement Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var DATA_TYPE
    # The data type object instance.
    DATA_TYPE = bool


class EventedMeasurement(StatefulMeasurement):
    """Evented Measurement Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var DATA_TYPE
    # The data type object instance.
    DATA_TYPE = unicode


class PercentageMeasurement(NumericMeasurement):
    """Percentage Measurement
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(0, 100)
    ## @var unit
    # The unit object instance.
    unit = units.Percentage

class AcceleratorPedalPosition(PercentageMeasurement):
    """Accelerator Pedal Position Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "accelerator_pedal_position"

class FuelLevel(PercentageMeasurement):
    """Fuel Level Class
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "fuel_level"

class VehicleSpeed(NumericMeasurement):
    """Vehicle Speed Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "vehicle_speed"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(0, 321)
    ## @var unit
    # The unit object instance.
    unit = units.KilometersPerHour

class EngineSpeed(NumericMeasurement):
    """Engine Speed Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "engine_speed"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(0, 8000)
    ## @var unit
    # The 8nit object instance.
    unit = units.RotationsPerMinute

class FuelConsumed(NumericMeasurement):
    """Fuel Consumed
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "fuel_consumed_since_restart"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(0, 100)
    ## @var unit
    # The unit object instance.
    unit = units.Litre

class Latitude(NumericMeasurement):
    """Latitude Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "latitude"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(-90, 90)
    ## @var unit
    # The unit object instance.
    unit = units.Degree

class Longitude(NumericMeasurement):
    """Longitude Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "longitude"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(-180, 180)
    ## @var unit
    # The unit object instance.
    unit = units.Degree

class Odometer(NumericMeasurement):
    """Odometer Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "odometer"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(0, 1000000)
    ## @var unit
    # The unit object instance.
    unit = units.Kilometer

class SteeringWheelAngle(NumericMeasurement):
    """SteeringWheelAngle Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "steering_wheel_angle"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(-600, 600)
    ## @var unit
    # The unit object instance.
    unit = units.Degree

class TorqueAtTransmission(NumericMeasurement):
    """Torque At Transmission Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "torque_at_transmission"
    ## @var valid_range
    # The valid_range object instance.
    valid_range = Range(-800, 1500)
    ## @var unit
    # The unit object instance.
    unit = units.NewtonMeter

class LateralAcceleration(NumericMeasurement):
    """Lateral Acceleration Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "lateral_acceleration"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(-5, 5)
    ## @var unit
    # The unit object instance.
    unit = units.MetersPerSecondSquared

class LongitudinalAcceleration(NumericMeasurement):
    """Longitudinal Acceleration Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "longitudinal_acceleration"
    ## @var valid_range
    # The valid range object instance.
    valid_range = Range(-5, 5)
    ## @var unit
    # The unit object instance.
    unit = units.MetersPerSecondSquared


class BrakePedalStatus(BooleanMeasurement):
    """Brake Pedal Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "brake_pedal_status"

class HeadlampStatus(BooleanMeasurement):
    """Headlamp Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "headlamp_status"

class HighBeamStatus(BooleanMeasurement):
    """High Beam Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "high_beam_status"

class ParkingBrakeStatus(BooleanMeasurement):
    """Parking Brake Status
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "parking_brake_status"

class WindshieldWiperStatus(BooleanMeasurement):
    """Windshield Wiper Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "windshield_wiper_status"


class IgnitionStatus(StatefulMeasurement):
    """Ignition Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "ignition_status"
    ## @var states
    # The states object instance.
    states = ['off', 'accessory', 'run', 'start']

class TransmissionGearPosition(StatefulMeasurement):
    """Transmission Gear Position
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "transmission_gear_position"
    ## @var states
    # The states object instance.
    states = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
            'eighth', 'neutral', 'reverse', 'park']

class TurnSignalStatus(StatefulMeasurement):
    """Turn Signal Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "turn_signal_status"

class ButtonEvent(EventedMeasurement):
    """Button Event Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    ## @var states
    # The states object instance.
    name = "button_event"
    states = ['up', 'down', 'left', 'right', 'ok']

class DoorStatus(EventedMeasurement):
    """Door Status Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var name
    # The name object instance.
    name = "door_status"
    ## @var states
    # The states object instance.
    states = ['driver', 'rear_left', 'rear_right', 'passenger']

class UnrecognizedMeasurementError(Exception):
    """Unrecognized Measurement Error Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    pass
