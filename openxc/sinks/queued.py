from .base import DataSink

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue

class QueuedSink(DataSink):
    def __init__(self):
        super(QueuedSink, self).__init__()
        self.queue = Queue()

    def receive(self, message, **kwargs):
        self.queue.put(message)
