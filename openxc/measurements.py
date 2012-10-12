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
    name = "vehicle_speed"


class UnrecognizedMeasurementError(Exception):
    pass

"""For a given measurement class, return the generic name. If the class does not
have a valid generic name, raises an UnrecognizedMeasurementError.
"""
def name_from_class(measurement_class):
    try:
        measurement_id = getattr(measurement_class, 'name')
    except AttributeError:
        raise UnrecognizedMeasurementError()
    else:
        return measurement_id
