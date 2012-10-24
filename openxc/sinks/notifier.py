from threading import Thread
from collections import defaultdict

from openxc.measurements import Measurement
from .base import DataSink

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue

class MeasurementNotifierSink(DataSink):
    def __init__(self):
        super(MeasurementNotifierSink, self).__init__()
        self.queue = Queue()
        self.callbacks = defaultdict(set)
        self.notifier = self.Notifier(self.queue, self._propagate)

    def register(self, measurement_class, callback):
        self.callbacks[Measurement.name_from_class(measurement_class)
                ].add(callback)

    def unregister(self, measurement_class, callback):
        self.callbacks[Measurement.name_from_class(measurement_class)
                ].remove(callback)

    def receive(self, message, **kwargs):
        self.queue.put((Measurement.from_dict(message), kwargs))

    def _propagate(self, measurement, **kwargs):
        for callback in self.callbacks[measurement.name]:
            callback(measurement, **kwargs)

    class Notifier(Thread):
        def __init__(self, queue, callback):
            super(MeasurementNotifierSink.Notifier, self).__init__()
            self.daemon = True
            self.queue = queue
            self.callback = callback
            self.start()

        def run(self):
            while True:
                measurement, kwargs = self.queue.get()
                self.callback(measurement, **kwargs)
                self.queue.task_done()