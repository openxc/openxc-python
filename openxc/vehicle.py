from .measurements import Measurement
from .sinks.base import MeasurementNotifierSink

class Vehicle(object):

    def __init__(self, source=None):
        self.sources = set()
        self.sinks = set()
        self.measurements = {}
        self.add_source(source)

        self.notifier = MeasurementNotifierSink()
        self.sinks.add(self.notifier)

    def get(self, measurement_class):
        name = Measurement.name_from_class(measurement_class)
        return self._construct_measurement(name)

    def listen(self, measurement_class, listener):
        self.notifier.register(measurement_class, listener)

    def unlisten(self, measurement_class, listener):
        self.notifier.unregister(measurement_class, listener)

    def _receive(self, message, **kwargs):
        name = message['name']
        self.measurements[name] = message

        for sink in self.sinks:
            sink.receive(message, **kwargs)

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
