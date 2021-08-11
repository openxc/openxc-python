"""A data source for reading from pre-recorded OpenXC trace files."""



import logging
import time

from .base import DataSourceError, BytestreamDataSource

from openxc.formats.json import JsonFormatter

LOG = logging.getLogger(__name__)

class TraceDataSource(BytestreamDataSource):
    """A class to replay a previously recorded OpenXC vehicle data trace file.
    For details on the trace file format, see
    http://openxcplatform.com/android/testing.html.
    """

    def __init__(self, filename=None, realtime=True, loop=True, **kwargs):
        """Construct the source and attempt to open the trace file.

            filename - the full absolute path to the trace file

            realtime - if ``True``, the trace will be replayed at approximately
            the same cadence as it was recorded. Otherwise, the trace file
            will be replayed as fast as possible (likely much faster than
            any vehicle).

            loop - if ``True``, the trace file will be looped and will provide
            data until the process exist or the source is stopped.
        """
        super(TraceDataSource, self).__init__(**kwargs)
        self.realtime = realtime
        self.loop = loop
        self.filename = filename
        self._reopen_file()

    def _reopen_file(self):
        if getattr(self, 'trace_file', None) is not None:
            self.trace_file.close()
        self.trace_file = self._open_file(self.filename)
        self.starting_time = time.time()

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
        line = self.trace_file.readline()
        if line == '':
            if self.loop:
                self._reopen_file()
            else:
                self.trace_file.close()
                self.trace_file = None
                raise DataSourceError()

        message = JsonFormatter.deserialize(line)
        timestamp = message.get('timestamp', None)
        if self.realtime and timestamp is not None:
            self._store_timestamp(timestamp)
            self._wait(self.starting_time, self.first_timestamp, timestamp)
        return (line + "\x00").encode("cp437")

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
