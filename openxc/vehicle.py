"""This module is contains the Vehicle class, which is the main entry point for
using the Python library to access vehicle data programatically. Most users will
want to interact with an instance of Vehicle, and won't need to deal with other
parts of the library directly (besides measurement types).
"""
from .measurements import Measurement
from .sinks import MeasurementNotifierSink

class Vehicle(object):
    """The Vehicle class is the main entry point for the OpenXC Python library.
    A Vehicle represents a connection to at least one vehicle data source and
    zero or 1 vehicle controllers, which can accept commands to send back to the
    vehicle. A Vehicle instance can have more than one data source (e.g. if the
    computer using this library has a secondary GPS data source).

    Most applications will either request synchronous vehicle data measurements
    using the ``get`` method or or with a callback function passed to
    ``listen``.

    More advanced applications that want access to all raw vehicle data may want
    to register a ``DataSink`` with a Vehicle.
    """

    def __init__(self, interface=None):
        """Construct a new Vehicle instance, optionally providing an vehicle
        interface from ``openxc.interface`` to user for I/O.
        """
        self.sources = set()
        self.sinks = set()
        self.measurements = {}

        if interface is not None:
            self.add_source(interface)
            self.controller = interface

        self.notifier = MeasurementNotifierSink()
        self.sinks.add(self.notifier)

    def get(self, measurement_class):
        """Return the latest measurement for the given class or None if nothing
        has been received from the vehicle.
        """
        name = Measurement.name_from_class(measurement_class)
        return self._construct_measurement(name)

    def listen(self, measurement_class, callback):
        """Register the callback function to be called whenever a new
        measurement of the given class is received from the vehicle data
        sources.

        If the callback is already registered for measurements of the given
        type, this method will have no effect.
        """
        self.notifier.register(measurement_class, callback)

    def unlisten(self, measurement_class, callback):
        """Stop notifying the given callback of new values of the measurement
        type.

        If the callback was not previously registered as a listener, this method
        will have no effect.
        """
        self.notifier.unregister(measurement_class, callback)

    def add_source(self, source):
        """Add a vehicle data source to the instance.

        The Vehicle instance will be set as the callback of the source, and the
        source will be started if it is startable. (i.e. it has a ``start()``
        method).
        """
        if source is not None:
            self.sources.add(source)
            source.callback = self._receive
            if hasattr(source, 'start'):
                source.start()

    def add_sink(self, sink):
        """Add a vehicle data sink to the instance. ``sink`` should be a
        sub-class of ``DataSink`` or at least have a ``receive(message,
        **kwargs)`` method.

        The sink will be started if it is startable. (i.e. it has a ``start()``
        method).
        """
        if sink is not None:
            self.sinks.add(sink)
            if hasattr(sink, 'start'):
                sink.start()

    def _receive(self, message, **kwargs):
        name = message.get('name', 'can_message')
        self.measurements[name] = message

        for sink in self.sinks:
            sink.receive(message, **kwargs)

    def _construct_measurement(self, measurement_id):
        raw_measurement = self.measurements.get(measurement_id, None)
        if raw_measurement is not None:
            return Measurement.from_dict(raw_measurement)
