"""Common functinality for data sinks that work on a queue of incoming
messages.
"""
from .base import DataSink

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue

class QueuedSink(DataSink):
    """Store every message received and any kwargs from the originating data
    source as a tuple in a queue.

    The queue can be reference in subclasses via the `queue` attribute.
    """
    
    ## @var queue
    # The queue object instance.
    
    def __init__(self):
        """Initialization Routine"""
        super(QueuedSink, self).__init__()
        self.queue = Queue()

    def receive(self, message, **kwargs):
        """Add the `message` and `kwargs` to the queue.
        @param message The received message.
        @param kwargs Additional input."""
        self.queue.put((message, kwargs))
