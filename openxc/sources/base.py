"""Abstract base interface for vehicle data sources."""


import threading
import logging
import string
import sys
import datetime

from openxc.formats.binary import ProtobufStreamer, ProtobufFormatter
from openxc.formats.json import JsonStreamer, JsonFormatter

LOG = logging.getLogger(__name__)

class MissingPayloadFormatError(Exception): pass

class DataSource(threading.Thread):
    """Interface for all vehicle data sources. This inherits from Thread and
    when a source is added to a vehicle it attempts to call the ``start()``
    method if it exists. If an implementer of DataSource needs some background
    process to read data, it's just a matter of defining a ``run()`` method.

    A data source requires a callback method to be specified. Whenever new data
    is received, it will pass it to that callback.
    """
    def __init__(self, callback=None, log_mode=None, payload_format=None):
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
        self._streamer = None
        self._formatter = None
        self._format = payload_format
        self.format = payload_format  # Added 7/30/2021 to fix protobuf streaming out

        self.logger = SourceLogger(self, log_mode)

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value
        if value == "json":
            self.streamer = JsonStreamer()
            self.formatter = JsonFormatter
        elif value == "protobuf":
            self.streamer = ProtobufStreamer()
            self.formatter = ProtobufFormatter

    @property
    def streamer(self):
        if self._streamer is None:
            raise MissingPayloadFormatError("Unable to auto-detect payload "
                "format, must specify manually with --format [json|protobuf]")
        return self._streamer

    @streamer.setter
    def streamer(self, value):
        self._streamer = value

    @property
    def formatter(self):
        if self._formatter is None:
            raise MissingPayloadFormatError("Unable to auto-detect payload "
                "format, must specify manually with --format [json|protobuf]")
        return self._formatter

    @formatter.setter
    def formatter(self, value):
        self._formatter = value

    @property
    def bytes_received(self):
        return self.streamer.bytes_received

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
            self.file = open(filename, 'w')

    def stop(self):
        self.running = False

    def record(self, message):
        if self.mode is not None and self.mode != "off" and len(message) > 0:
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
        message_buffer = ""
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
                record, _, remainder = message_buffer.partition("\x00")
                self.record(record)
                message_buffer = remainder


class BytestreamDataSource(DataSource):
    """A source that receives data is a series of bytes, with discrete messages
    separated by a newline character.

    Subclasses of this class need only to implement the ``read`` method.
    """

    def __init__(self, **kwargs):
        super(BytestreamDataSource, self).__init__(**kwargs)
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

    def parse_messages(self):
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

    def run(self):
        """Continuously read data from the source and attempt to parse a valid
        message from the buffer of bytes. When a message is parsed, passes it
        off to the callback if one is set.
        """
        while self.running:
            payload = ""
            payloadsave = ""
            try:
                payload = self.read()
                try:
                    payloadsave = str(payload, "cp437", "ignore")
                except:
                    payloadsave = ""
            except DataSourceError as e:
                if self.running:
                    LOG.warn("Can't read from data source -- stopping: %s", e)
                break

            try:
                self.streamer
            except MissingPayloadFormatError:
                json_chars = ['\x00']
                json_chars.extend(string.printable)
                if all((char in json_chars for char in payloadsave)):
                    self.format = "json"
                else:
                    self.format = "protobuf"
            self.streamer.receive(payload)
            self.parse_messages()

    def _receive_command_response(self, message):
        # TODO the controller/source are getting a little mixed up since the
        # controller now needs to receive responses from the soruce side, maybe
        # just mix them again. the only exception to being both is a trace
        # source, and we can just leave the controller methods on that
        # unimplemented
        self.open_requests = getattr(self, 'open_requests', [])
        for open_request in self.open_requests:
            open_request.put(message)


class DataSourceError(Exception):
    pass
