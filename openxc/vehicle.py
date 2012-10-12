from collections import defaultdict

import openxc.measurements as measurements
from .measurements import Measurement

class Vehicle(object):

    def __init__(self, source=None):
        self.sources = set()
        self.measurements = {}

        self.add_source(source)
        self.listeners = defaultdict(set)

    def get(self, measurement_class):
        name = measurements.name_from_class(measurement_class)
        return self._construct_measurement(name)

    def listen(self, measurement_class, listener):
        self.listeners[measurement_class.name].add(listener)

    def unlisten(self, measurement_class, listener):
        self.listeners[measurement_class.name].remove(listener)

    def _receive(self, message):
        name = message['name']
        self.measurements[name] = message
        if name in self.listeners:
            measurement = self._construct_measurement(name)
            for listener in self.listeners[name]:
                listener(measurement)

    def _construct_measurement(self, measurement_id):
        raw_measurement = self.measurements.get(measurement_id, None)
        if raw_measurement is not None:
            return Measurement.from_dict(raw_measurement)

    def add_source(self, source):
        if source is not None:
            self.sources.add(source)
            source.callback = self._receive
            source.start()
