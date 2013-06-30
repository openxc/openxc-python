"""Trace file recording operations."""
from threading import Thread
import datetime
import time

from openxc.formats import JsonFormatter
from .queued import QueuedSink


class FileRecorderSink(QueuedSink):
    """A sink to record trace files based on the messages received from all data
    sources.
    """
    
    ## @var FILENAME_DATE_FORMAT
    # The filename date format string
    FILENAME_DATE_FORMAT = "%Y-%m-%d-%H"
    ## @var FILENAME_FORMAT
    # The JSON filename format.
    FILENAME_FORMAT = "%s.json"
    
    ## @var recorder
    # The recorder object instance.
    
    def __init__(self):
        """Initialization Routine"""
        super(FileRecorderSink, self).__init__()
        self.recorder = self.Recorder(self.queue)

    class Recorder(Thread):
        """Recorder Class"""
        
        ## @var daemon
        # The daemon object value.
        ## @var queue
        # The queue object instance.
        
        def __init__(self, queue):
            """Initialization Routine
            @param queue The queue object instance."""
            super(FileRecorderSink.Recorder, self).__init__()
            self.daemon = True
            self.queue = queue
            self.start()

        @staticmethod
        def _generate_filename():
            """Generate Filename Routine
            @return The generated filename string."""
            current_date = datetime.datetime.now()
            return FileRecorderSink.FILENAME_FORMAT % current_date.strftime(
                    FileRecorderSink.FILENAME_DATE_FORMAT)

        def run(self):
            """Run Routine"""
            while True:
                last_hour_opened = datetime.datetime.now().hour
                filename = self._generate_filename()
                with open(filename, 'a') as output_file:
                    while True:
                        message, _ = self.queue.get()
                        message['timestamp'] = time.time()
                        output_file.write(JsonFormatter.serialize(message))
                        self.queue.task_done()

                        if datetime.datetime.now().hour > last_hour_opened:
                            break
