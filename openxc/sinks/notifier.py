"""A data sink implementation for the core listener notification service of
:class:`openxc.vehicle.Vehicle`.
"""
from threading import Thread
from collections import defaultdict

from openxc.measurements import Measurement
from .queued import QueuedSink


class MeasurementNotifierSink(QueuedSink):
    """Notify previously registered callbacks whenever measurements of a certian
    type have been received.

    This data sink is the core of the asynchronous interface of
    :class:`openxc.vehicle.Vehicle.`
    """
    def __init__(self):
        super(MeasurementNotifierSink, self).__init__()
        self.callbacks = defaultdict(set)
        self.notifier = self.Notifier(self.queue, self._propagate)

    def register(self, measurement_class, callback):
        """Call the ``callback`` with any new values of ``measurement_class``
        received.
        """
        self.callbacks[Measurement.name_from_class(measurement_class)
                ].add(callback)

    def unregister(self, measurement_class, callback):
        """Stop notifying ``callback`` of new values of ``measurement_class``.

        If the callback wasn't previously registered, this method will have no
        effect.
        """
        self.callbacks[Measurement.name_from_class(measurement_class)
                ].remove(callback)

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
                message, kwargs = self.queue.get()
                try:
                    measurement = Measurement.from_dict(message)
                    self.callback(measurement, **kwargs)
                    self.queue.task_done()
                except MeasurementError as e:
                    # TODO add some logging
                    pass
