import numbers

from .utils import Range

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str


class Measurement(object):
    DATA_TYPE = numbers.Number
    _measurement_map = {}

    def __init__(self, name, value, event=None):
        self.name = name
        self.value = value
        self.event = event

    @classmethod
    def from_dict(cls, data):
        measurement_class = cls._class_from_name(data['name'])
        return measurement_class(data['name'], data['value'],
                data.get('event', None))

    @classmethod
    def _class_from_name(cls, measurement_name):
        return cls._measurement_map[measurement_name]

    @classmethod
    def name_from_class(cls, measurement_class):
        """For a given measurement class, return the generic name. If the class
        does not have a valid generic name, raises an
        UnrecognizedMeasurementError.
        """
        try:
            name = getattr(measurement_class, 'name')
        except AttributeError:
            raise UnrecognizedMeasurementError()
        else:
            cls._measurement_map[name] = measurement_class
            return name


class NumericMeasurement(Measurement):
    valid_range = None


class StatefulMeasurement(Measurement):
    DATA_TYPE = unicode
    states = None

class BooleanMeasurement(Measurement):
    DATA_TYPE = bool

class EventedMeasurement(StatefulMeasurement):
    DATA_TYPE = unicode

    def valid_state(self):
        return self.value in self.states


class PercentageMeasurement(NumericMeasurement):
    valid_range = Range(0, 100)


class AcceleratorPedalPosition(PercentageMeasurement):
    name = "accelerator_pedal_position"

class FuelLevel(PercentageMeasurement):
    name = "fuel_level"


class VehicleSpeed(NumericMeasurement):
    name = "vehicle_speed"
    valid_range = Range(0, 321)

class EngineSpeed(NumericMeasurement):
    name = "engine_speed"
    valid_range = Range(0, 8000)

class FineOdometer(NumericMeasurement):
    name = "fine_odometer_since_restart"
    valid_range = Range(0, 1000)

class FuelConsumed(NumericMeasurement):
    name = "fuel_consumed_since_restart"
    valid_range = Range(0, 100)

class Latitude(NumericMeasurement):
    name = "latitude"
    valid_range = Range(-90, 90)

class Longitude(NumericMeasurement):
    name = "longitude"
    valid_range = Range(-180, 180)

class Odometer(NumericMeasurement):
    name = "odometer"
    valid_range = Range(0, 1000000)

class SteeringWheelAngle(NumericMeasurement):
    name = "steering_wheel_angle"
    valid_range = Range(-600, 600)

class TorqueAtTransmission(NumericMeasurement):
    name = "torque_at_transmission"
    valid_range = Range(-800, 1500)

class LateralAcceleration(NumericMeasurement):
    name = "lateral_acceleration"
    valid_range = Range(-5, 5)

class LongitudinalAcceleration(NumericMeasurement):
    name = "lognitudinal_acceleration"
    valid_range = Range(-5, 5)


class BrakePedalStatus(BooleanMeasurement):
    name = "brake_pedal_status"

class HeadlampStatus(BooleanMeasurement):
    name = "headlamp_status"

class HighBeamStatus(BooleanMeasurement):
    name = "high_beam_status"

class ParkingBrakeStatus(BooleanMeasurement):
    name = "parking_brake_status"

class WindshieldWiperStatus(BooleanMeasurement):
    name = "windshield_wiper_status"


class IgnitionStatus(StatefulMeasurement):
    name = "ignition_status"
    states = ['off', 'accessory', 'run', 'start']

class TransmissionGearPosition(StatefulMeasurement):
    name = "transmission_gear_position"
    states = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
            'eighth', 'neutral', 'reverse', 'park']

class GearLevelPosition(StatefulMeasurement):
    name = "gear_lever_position"
    states = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
            'neutral', 'reverse', 'park', 'drive', 'low', 'sport']

class TurnSignalStatus(StatefulMeasurement):
    name = "turn_signal_status"


class ButtonEvent(EventedMeasurement):
    name = "button_event"

class DoorStatus(EventedMeasurement):
    name = "door_status"
    states = ['driver', 'rear_left', 'rear_right', 'passenger']


class UnrecognizedMeasurementError(Exception):
    pass
