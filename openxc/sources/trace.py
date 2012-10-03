from __future__ import absolute_import

import logging
import time

from .base import DataSource, DataSourceError

LOG = logging.getLogger(__name__)

class TraceDataSource(DataSource):
    DEFAULT_PORT = "/dev/ttyUSB0"
    DEFAULT_BAUDRATE = 115200

    def __init__(self, callback, filename=None, realtime=True, loop=True):
        super(TraceDataSource, self).__init__(callback)
        self.realtime = realtime
        self.loop = loop
        self.filename = filename
        self.reopen_file()

    def reopen_file(self):
        if getattr(self, 'trace_file', None) is not None:
            self.trace_file.close()
        self.trace_file = self.open_file(self.filename)

    @classmethod
    def open_file(cls, filename):
        try:
            trace_file = open(filename, "r")
        except IOError as e:
            raise DataSourceError("Unable to open trace file %s" % filename, e)
        else:
            LOG.debug("Opened trace file %s", filename)
            return trace_file

    def wait(self, starting_time, timestamp):
        if getattr(self, 'first_timestamp', None) is None:
            self.first_timestamp = timestamp
            LOG.debug("Storing %d as the first timestamp of the trace file %s",
                    self.first_timestamp, self.filename)

        target_time = starting_time + (timestamp - self.first_timestamp)
        time.sleep(max(target_time - time.time(), 0))

    def read(self):
        return self.trace_file.readline()

    def run(self):
        while True:
            self.reopen_file()
            starting_time = time.time()

            while True:
                line = self.read()
                message, _, byte_count = self._parse_message(line)
                if message is None:
                    break

                self.bytes_received += byte_count
                if not self._validate(message):
                    continue
                if self.realtime and 'timestamp' in message:
                    self.wait(starting_time, message['timestamp'])
                self.callback(message)

            self.trace_file.close()
            self.trace_file = None

            if not self.loop:
                break

    def _validate(self, message):
        for key in ['name', 'value']:
            if key not in message:
                return False
        return True

    def _write(self, message):
        raise NotImplementedError("Can't send commands to a trace file")
