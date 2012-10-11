class Measurement(object):
    def __init__(self, name, value, event=None):
        self.name = name
        self.value = value
        self.event = event

    @classmethod
    def from_dict(cls, data):
        #TODO
        #measurement_class = class_for_name(
        return cls(data['name'], data['value'], data.get('event', None))


class VehicleSpeed(Measurement):
    NAME = "vehicle_speed"


class UnrecognizedMeasurementError(Exception):
    pass

{{
