from collections import defaultdict

from .measurements import Measurement

class Vehicle(object):

    def __init__(self, source=None):
        self.sources = set()
        self.sinks = set()
        self.measurements = {}
        self.listeners = defaultdict(set)
        self.add_source(source)

    def get(self, measurement_class):
        name = Measurement.name_from_class(measurement_class)
        return self._construct_measurement(name)

    def listen(self, measurement_class, listener):
        self.listeners[Measurement.name_from_class(measurement_class)
                ].add(listener)

    def unlisten(self, measurement_class, listener):
        self.listeners[Measurement.name_from_class(measurement_class)
                ].remove(listener)

    def _receive(self, message, **kwargs):
        name = message['name']
        self.measurements[name] = message

        # TODO this should be a sink
        measurement = self._construct_measurement(name)
        if measurement is not None:
            if name in self.listeners:
                for listener in self.listeners[name]:
                    listener(measurement)

            for sink in self.sinks:
                sink.receive(measurement, **kwargs)

    def _construct_measurement(self, measurement_id):
        raw_measurement = self.measurements.get(measurement_id, None)
        if raw_measurement is not None:
            return Measurement.from_dict(raw_measurement)

    def add_source(self, source):
        if source is not None:
            self.sources.add(source)
            source.callback = self._receive
            source.start()

    def add_sink(self, sink):
        if sink is not None:
            self.sinks.add(sink)
            if hasattr(sink, 'start'):
                sink.start()
