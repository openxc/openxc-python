from threading import Thread
from collections import defaultdict

from openxc.measurements import Measurement

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue


class DataSink(object):
    def receive(self, message):
        raise NotImplementedError("Don't use DataSink directly")


class MeasurementNotifierSink(DataSink):
    def __init__(self):
        super(MeasurementNotifierSink, self).__init__()
        self.queue = Queue()
        self.listeners = defaultdict(set)
        self.notifier = self.Notifier(self.queue, self._propagate)

    def register(self, measurement_class, listener):
        self.listeners[Measurement.name_from_class(measurement_class)
                ].add(listener)

    def unregister(self, measurement_class, listener):
        self.listeners[Measurement.name_from_class(measurement_class)
                ].remove(listener)

    def receive(self, message):
        measurement = Measurement.from_dict(message)
        if measurement is not None:
            if measurement.name in self.listeners:
                for listener in self.listeners[measurement.name]:
                    listener(measurement)

    def _propagate(self, measurement):
        for listener in self.listeners:
            listener.receive(measurement)


    class Notifier(Thread):
        def __init__(self, queue, callback):
            super(MeasurementNotifierSink.Notifier, self).__init__()
            self.daemon = True
            self.queue = queue
            self.callback = callback

        def run(self):
            while True:
                measurement = self.queue.get()
                self.callback(measurement)
                self.queue.task_done()
