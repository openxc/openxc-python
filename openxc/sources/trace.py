
"""
@file    openxc-python\openxc\sources\trace.py Trace Sources Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   A data source for reading from pre-recorded OpenXC trace files."""

from __future__ import absolute_import

import logging
import time

from .base import DataSourceError, BytestreamDataSource

## @var LOG
# The logging object instance.
LOG = logging.getLogger(__name__)

class TraceDataSource(BytestreamDataSource):
    """A class to replay a previously recorded OpenXC vehicle data trace file.
    For details on the trace file format, see
    http://openxcplatform.com/android/testing.html.
    
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var realtime
    # The realtime object instance.
    ## @var loop
    # The loop object instance.
    ## @var filename
    # The filename object instance.
    ## @var first_timestamp
    # The first_timestamp object instance.
    ## @var trace_file
    # The trace_file object instance.
    
    def __init__(self, callback=None, filename=None, realtime=True, loop=True):
        """Construct the source and attempt to open the trace file.

        Kwargs:
            filename - the full absolute path to the trace file
            realtime - if ``True``, the trace will be replayed at approximately
                the same cadence as it was recorded. Otherwise, the trace file 
                will be replayed as fast as possible (likely much faster than 
                any vehicle).
            loop - if ``True``, the trace file will be looped and will provide
                data until the process exist or the source is stopped.
        
        @param callback the callback function.
        @param filename the full absolute path to the trace file
        @param realtime if ``True``, the trace will be replayed at 
                approximately the same cadence as it was recorded. Otherwise, 
                the trace file will be replayed as fast as possible (likely 
                much faster than any vehicle).
        @param loop the loop object instance.
        """
        super(TraceDataSource, self).__init__(callback)
        self.realtime = realtime
        self.loop = loop
        self.filename = filename
        self._reopen_file()

    def run(self):
        """Run Routine"""
        while True:
            self._reopen_file()
            starting_time = time.time()

            while True:
                line = self._read()
                message, _, byte_count = self._parse_message(line)
                if message is None:
                    continue

                self.bytes_received += byte_count
                if not self._validate(message):
                    continue
                timestamp = message.get('timestamp', None)
                if self.realtime and 'timestamp' is not None:
                    self._store_timestamp(timestamp)
                    self._wait(starting_time, self.first_timestamp, timestamp)
                if self.callback is not None:
                    self.callback(message)

            self.trace_file.close()
            self.trace_file = None

            if not self.loop:
                break

    def _reopen_file(self):
        """Reopen File Routine"""
        if getattr(self, 'trace_file', None) is not None:
            self.trace_file.close()
        self.trace_file = self._open_file(self.filename)

    def _store_timestamp(self, timestamp):
        """If not already saved, cache the first timestamp in the active trace
        file on the instance.
        @param timestamp The timestamp object instance.
        """
        if getattr(self, 'first_timestamp', None) is None:
            self.first_timestamp = timestamp
            LOG.debug("Storing %d as the first timestamp of the trace file %s",
                    self.first_timestamp, self.filename)

    def _read(self):
        """Read a line of data from the input source at a time."""
        return self.trace_file.readline()

    @staticmethod
    def _open_file(filename):
        """Attempt to open the the file at ``filename`` for reading.

        Raises:
            DataSourceError, if the file cannot be opened.
            
        @param filename The file name to open for reading.
        """
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
        @param starting_time The starting timestamp object instance.
        #param first_timestamp The first timestamp object instance.
        @param timestamp The timestamp object instance."""
        target_time = starting_time + (timestamp - first_timestamp)
        time.sleep(max(target_time - time.time(), 0))

    @staticmethod
    def _validate(message):
        """Confirm the validitiy of a given dict as an OpenXC message.

        Returns:
            ``True`` if the message contains at least a ``name`` and ``value``.
        @param message The message instance.
        """
        # Flag to determine return value (for single point of return)
        flag = True
        # Loop through each key as a name and value pair
        for key in ['name', 'value']:
            # Might loop extra times, although it only has one point of return.
            if flag and key not in message:
                # Update flag for single point of return.
                flag = False
        # Return the flag value as part of single point of return
        return flag
