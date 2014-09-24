"""Abstract base interface for vehicle data sources."""
from __future__ import print_function

import threading
import logging
import string
import sys
import datetime

from openxc.formats.binary import BinaryStreamer, BinaryFormatter
from openxc.formats.json import JsonStreamer, JsonFormatter

LOG = logging.getLogger(__name__)


class DataSource(threading.Thread):
    """Interface for all vehicle data sources. This inherits from Thread and
    when a source is added to a vehicle it attempts to call the ``start()``
    method if it exists. If an implementer of DataSource needs some background
    process to read data, it's just a matter of defining a ``run()`` method.

    A data source requires a callback method to be specified. Whenever new data
    is received, it will pass it to that callback.
    """
    def __init__(self, callback=None, log_mode=None, format=None):
        """Construct a new DataSource.

        By default, DataSource threads are marked as ``daemon`` threads, so they
        will die as soon as all other non-daemon threads in the process have
        quit.

        Kwargs:
            callback - function to call with any new data received
        """
        super(DataSource, self).__init__()
        self.callback = callback
        self.daemon = True
        self.running = True

        self.streamer = None
        if format == "json":
            self.streamer = JsonStreamer()
            self.formatter = JsonFormatter
        elif format == "binary":
            self.streamer = BinaryStreamer()
            self.formatter = BinaryFormatter

        self.logger = SourceLogger(self, log_mode)

    def start(self):
        self.logger.start()
        super(DataSource, self).start()

    def stop(self):
        self.logger.stop()
        self.running = False

    def read(self, timeout=None):
        """Read data from the source.

        Kwargs:
            timeout (float) - if the source implementation could potentially
                block, timeout after this number of seconds.
        """
        raise NotImplementedError("Don't use DataSource directly")

    def read_logs(self, timeout=None):
        """Read log data from the source.

        Kwargs:
            timeout (float) - if the source implementation could potentially
                block, timeout after this number of seconds.
        """
        raise NotImplementedError("Don't use DataSource directly")


class SourceLogger(threading.Thread):
    FILENAME_TEMPLATE = "%d-%m-%Y.%H-%M-%S"

    def __init__(self, source, mode="off"):
        super(SourceLogger, self).__init__()
        self.daemon = True
        self.source = source
        self.mode = mode
        self.file = None
        self.running = True

        if self.mode == "file":
            filename = "openxc-logs-%s.txt" % datetime.datetime.now().strftime(
                    self.FILENAME_TEMPLATE)
            self.file = open(filename, 'wa')

    def stop(self):
        self.running = False

    def record(self, message):
        if self.mode != "off" and len(message) > 0:
            log_file = None
            if self.mode == "stderr":
                log_file = sys.stderr
            elif self.mode == "file" and self.file is not None:
                log_file = self.file
            print("LOG: %s" % message, file=log_file)

    def run(self):
        """Continuously read data from the source and attempt to parse a valid
        message from the buffer of bytes. When a message is parsed, passes it
        off to the callback if one is set.
        """
        message_buffer = b""
        while self.running:
            try:
                message_buffer += self.source.read_logs()
            except DataSourceError as e:
                if self.running:
                    LOG.warn("Can't read logs from data source -- stopping: %s", e)
                break
            except NotImplementedError as e:
                LOG.info("%s doesn't support logging" % self)
                break

            while True:
                if "\x00" not in message_buffer:
                    break
                record, _, remainder = message_buffer.partition(b"\x00")
                self.record(record)
                message_buffer = remainder


class BytestreamDataSource(DataSource):
    """A source that receives data is a series of bytes, with discrete messages
    separated by a newline character.

    Subclasses of this class need only to implement the ``read`` method.
    """

    def __init__(self, callback=None, log_mode=None, **kwargs):
        super(BytestreamDataSource, self).__init__(callback, log_mode, **kwargs)
        self.bytes_received = 0
        self.corrupted_messages = 0
        self.running = True

    def _message_valid(self, message):
        if not hasattr(message, '__iter__'):
            return False
        if not ('name' in message and 'value' in message or
                    ('id' in message and 'data' in message) or
                    ('id' in message and 'bus' in message) or
                    'command_response' in message):
            return False
        return True

    def run(self):
        """Continuously read data from the source and attempt to parse a valid
        message from the buffer of bytes. When a message is parsed, passes it
        off to the callback if one is set.
        """
        while self.running:
            try:
                payload = self.read()
            except DataSourceError as e:
                if self.running:
                    LOG.warn("Can't read from data source -- stopping: %s", e)
                break

            if self.streamer is None:
                json_chars = ['\x00']
                json_chars.extend(string.printable)
                if all((char in json_chars for char in payload)):
                    self.streamer = JsonStreamer()
                else:
                    self.streamer = BinaryStreamer()
            self.streamer.receive(payload)

            while True:
                message = self.streamer.parse_next_message()
                if message is None:
                    break

                if not self._message_valid(message):
                    self.corrupted_messages += 1
                    break

                if self.callback is not None:
                    self.callback(message)
                self._receive_command_response(message)

    def _receive_command_response(self, message):
        # TODO the controller/source are getting a litlte mixed up since the
        # controller now needs to receive responses from the soruce side, maybe
        # just mix them again. the only exception to being both is a trace
        # source, and we can just leave the controller methods on that
        # unimplemented
        self.open_requests = getattr(self, 'open_requests', [])
        for open_request in self.open_requests:
            open_request.put(message)


class DataSourceError(Exception):
    pass
