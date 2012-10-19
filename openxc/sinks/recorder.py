from threading import Thread
import datetime
import time

from openxc.formats import JsonFormatter
from .base import DataSink

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue


class FileRecorderSink(DataSink):
    FILENAME_DATE_FORMAT = "%Y-%m-%d-%H"
    FILENAME_FORMAT = "%s.json"

    def __init__(self):
        super(FileRecorderSink, self).__init__()
        self.queue = Queue()
        self.recorder = self.Recorder(self.queue)

    def receive(self, message, **kwargs):
        self.queue.put(message)

    class Recorder(Thread):
        def __init__(self, queue):
            super(FileRecorderSink.Recorder, self).__init__()
            self.daemon = True
            self.queue = queue
            self.start()

        @staticmethod
        def _generate_filename():
            current_date = datetime.datetime.now()
            return FileRecorderSink.FILENAME_FORMAT % current_date.strftime(
                    FileRecorderSink.FILENAME_DATE_FORMAT)


        def run(self):
            while True:
                last_hour_opened = datetime.datetime.now().hour
                filename = self._generate_filename()
                with open(filename, 'a') as output_file:
                    while True:
                        message = self.queue.get()
                        message['timestamp'] = time.time()
                        output_file.write(JsonFormatter.serialize(message))
                        self.queue.task_done()

                        if datetime.datetime.now().hour > last_hour_opened:
                            break
