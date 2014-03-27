"""A data source for reading from pre-recorded OpenXC trace files."""

from __future__ import absolute_import

import logging
import time

from .base import DataSourceError, BytestreamDataSource

LOG = logging.getLogger(__name__)

class TraceDataSource(BytestreamDataSource):
    """A class to replay a previously recorded OpenXC vehicle data trace file.
    For details on the trace file format, see
    http://openxcplatform.com/android/testing.html.
    """

    def __init__(self, callback=None, filename=None, realtime=True, loop=True,
            **kwargs):
        """Construct the source and attempt to open the trace file.

        Kwargs:
            filename - the full absolute path to the trace file

            realtime - if ``True``, the trace will be replayed at approximately
            the same cadence as it was recorded. Otherwise, the trace file
            will be replayed as fast as possible (likely much faster than
            any vehicle).

            loop - if ``True``, the trace file will be looped and will provide
            data until the process exist or the source is stopped.
        """
        super(TraceDataSource, self).__init__(callback)
        self.realtime = realtime
        self.loop = loop
        self.filename = filename

    def run(self):
        while True:
            self._reopen_file()
            starting_time = time.time()

            while True:
                line = self.read()
                if line == '':
                    break

                message, _, byte_count = self._parse_message(line + '\x00')
                if message is None:
                    continue

                self.bytes_received += byte_count
                if not self._validate(message):
                    continue
                timestamp = message.get('timestamp', None)
                if self.realtime and timestamp is not None:
                    self._store_timestamp(timestamp)
                    self._wait(starting_time, self.first_timestamp, timestamp)
                if self.callback is not None:
                    self.callback(message)

            self.trace_file.close()
            self.trace_file = None

            if not self.loop:
                break

    def _reopen_file(self):
        if getattr(self, 'trace_file', None) is not None:
            self.trace_file.close()
        self.trace_file = self._open_file(self.filename)

    def _store_timestamp(self, timestamp):
        """If not already saved, cache the first timestamp in the active trace
        file on the instance.
        """
        if getattr(self, 'first_timestamp', None) is None:
            self.first_timestamp = timestamp
            LOG.debug("Storing %d as the first timestamp of the trace file %s",
                    self.first_timestamp, self.filename)

    def read(self):
        """Read a line of data from the input source at a time."""
        return self.trace_file.readline()

    @staticmethod
    def _open_file(filename):
        """Attempt to open the the file at ``filename`` for reading.

        Raises:
            DataSourceError, if the file cannot be opened.
        """
        if filename is None:
            raise DataSourceError("Trace filename is not defined")

        try:
            trace_file = open(filename, "r")
        except IOError as e:
            raise DataSourceError("Unable to open trace file %s" % filename, e)
        else:
            LOG.debug("Opened trace file %s", filename)
            return trace_file

    @staticmethod
    def _wait(starting_time, first_timestamp, timestamp):
        """Given that the first timestamp in the trace file is
        ``first_timestamp`` and we started playing back the file at
        ``starting_time``, block until the current ``timestamp`` should occur.
        """
        target_time = starting_time + (timestamp - first_timestamp)
        time.sleep(max(target_time - time.time(), 0))

    @staticmethod
    def _validate(message):
        """Confirm the validitiy of a given dict as an OpenXC message.

        Returns:
            ``True`` if the message contains at least a ``name`` and ``value``.
        """
        valid = False
        if(('name' in message and 'value' in message) or
                ('id' in message and 'data' in message)):
            valid = True
        return valid
