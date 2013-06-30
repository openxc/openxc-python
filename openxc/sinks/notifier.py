"""A data sink implementation for the core listener notification service of
:class:`openxc.vehicle.Vehicle`.
"""
from threading import Thread
from collections import defaultdict

from openxc.measurements import Measurement, UnrecognizedMeasurementError
from .queued import QueuedSink


class MeasurementNotifierSink(QueuedSink):
    """Notify previously registered callbacks whenever measurements of a certian
    type have been received.

    This data sink is the core of the asynchronous interface of
    :class:`openxc.vehicle.Vehicle.`
    """
    
    ## @var callbacks
    # List of callback routines.
    ## @var notifier
    # The notifier object instance.
    
    def __init__(self):
        """Initialization Routine"""
        super(MeasurementNotifierSink, self).__init__()
        self.callbacks = defaultdict(set)
        self.notifier = self.Notifier(self.queue, self._propagate)

    def register(self, measurement_class, callback):
        """Call the ``callback`` with any new values of ``measurement_class``
        received.
        @param measurement_class The measurement class for this object 
        instance.
        @param callback the callback function name.
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
        """Propagate Routine
        @param measurement to send to the callback routine(s).
        @param kwargs Additional input to send to callback routine(s)."""
        for callback in self.callbacks[measurement.name]:
            try:
                callback(measurement, **kwargs)
            except TypeError:
                callback(measurement)

    class Notifier(Thread):
        """Notifier Class"""
        
        ## @var daemon
        # Boolean representing if the notifier functions as a daemon.
        ## @var queue
        # The queue object instance.
        ## @var callback
        # The name of the callback routine.
        
        def __init__(self, queue, callback):
            """Initialization Routine
            @param queue The queue object instance.
            @param callback The name of the callback."""
            super(MeasurementNotifierSink.Notifier, self).__init__()
            self.daemon = True
            self.queue = queue
            self.callback = callback
            self.start()

        def run(self):
            """Run Routine"""
            while True:
                message, kwargs = self.queue.get()
                try:
                    measurement = Measurement.from_dict(message)
                    self.callback(measurement, **kwargs)
                    self.queue.task_done()
                except UnrecognizedMeasurementError as e:
                    # TODO add some logging
                    pass
