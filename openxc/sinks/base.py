"""Common operations for all vehicle data sinks."""

class DataSink(object):
    """A base interface for all data sinks. At the minimum, a data sink must
    have a :func:`receive` method.
    """

    def receive(self, message, **kwargs):
        """Handle an incoming vehicle data message.

        Args:
            message (dict) - a new OpenXC vehicle data message

        Kwargs:
           data_remaining (bool) - if the originating data source can peek ahead
               in the data stream, this argument will True if there is more data
               available.
        """
        raise NotImplementedError("Don't use DataSink directly")
