"""Abstract base interface for vehicle data sources."""
from __future__ import print_function

import threading
import logging
import binascii
import google.protobuf.message
import string
import sys
import datetime
from google.protobuf.internal.decoder import _DecodeVarint

from openxc import openxc_pb2
from openxc.formats.json import JsonFormatter

LOG = logging.getLogger(__name__)


class DataSource(threading.Thread):
    """Interface for all vehicle data sources. This inherits from Thread and
    when a source is added to a vehicle it attempts to call the ``start()``
    method if it exists. If an implementer of DataSource needs some background
    process to read data, it's just a matter of defining a ``run()`` method.

    A data source requires a callback method to be specified. Whenever new data
    is received, it will pass it to that callback.
    """
    def __init__(self, callback=None, log_mode=None):
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
        self.logger = SourceLogger(self, log_mode)

    def start(self):
        self.logger.start()
        super(DataSource, self).start()

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

        if self.mode == "file":
            filename = "openxc-logs-%s.txt" % datetime.datetime.now().strftime(
                    self.FILENAME_TEMPLATE)
            self.file = open(filename, 'wa')

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
        while True:
            try:
                message_buffer += self.source.read_logs()
            except DataSourceError as e:
                LOG.warn("Can't read logs from data source -- stopping: %s", e)
                break
            except NotImplementedError as e:
                LOG.info("%s doesn't support logging" % self)
                break

            while True:
                if "\r\n" not in message_buffer:
                    break
                record, _, remainder = message_buffer.partition(b"\r\n")
                self.record(record)
                message_buffer = remainder


class BytestreamDataSource(DataSource):
    """A source that receives data is a series of bytes, with discrete messages
    separated by a newline character.

    Subclasses of this class need only to implement the ``read`` method.
    """

    MAX_PROTOBUF_MESSAGE_LENGTH = 200

    def __init__(self, callback=None, log_mode=None):
        super(BytestreamDataSource, self).__init__(callback, log_mode)
        self.bytes_received = 0
        self.corrupted_messages = 0

    def _message_valid(self, message):
        if not hasattr(message, '__iter__'):
            return False
        if not ('name' in message and 'value' in message or
                    ('id' in message and 'data' in message) or
                    ('id' in message and 'bus' in message)):
            return False
        return True

    def run(self):
        """Continuously read data from the source and attempt to parse a valid
        message from the buffer of bytes. When a message is parsed, passes it
        off to the callback if one is set.
        """
        message_buffer = b""
        while True:
            try:
                message_buffer += self.read()
            except DataSourceError as e:
                LOG.warn("Can't read from data source -- stopping: %s", e)
                break

            while True:
                message, message_buffer, byte_count = self._parse_message(
                        message_buffer)
                if message is None:
                    break
                if not self._message_valid(message):
                    self.corrupted_messages += 1
                    break

                self.bytes_received += byte_count
                if self.callback is not None:
                    self.callback(message)

    def _protobuf_to_dict(self, message):
        parsed_message = {}
        if message.type == message.RAW and message.HasField('raw_message'):
            raw_message = message.raw_message
            if raw_message.HasField('bus'):
                parsed_message['bus'] = raw_message.bus
            if raw_message.HasField('message_id'):
                parsed_message['id'] = raw_message.message_id
            if raw_message.HasField('data'):
                parsed_message['data'] = "0x%s" % binascii.hexlify(raw_message.data)
        elif message.type == message.DIAGNOSTIC:
            diagnostic_message = message.diagnostic_message
            if diagnostic_message.HasField('bus'):
                parsed_message['bus'] = diagnostic_message.bus
            if diagnostic_message.HasField('message_id'):
                parsed_message['id'] = diagnostic_message.message_id
            if diagnostic_message.HasField('mode'):
                parsed_message['mode'] = diagnostic_message.mode
            if diagnostic_message.HasField('pid'):
                parsed_message['pid'] = diagnostic_message.pid
            if diagnostic_message.HasField('success'):
                parsed_message['success'] = diagnostic_message.success
            if diagnostic_message.HasField('negative_response_code'):
                parsed_message['negative_response_code'] = diagnostic_message.negative_response_code
            if diagnostic_message.HasField('payload'):
                parsed_message['payload'] = "0x%s" % binascii.hexlify(diagnostic_message.payload)
        elif message.type == message.TRANSLATED:
            translated_message = message.translated_message
            parsed_message['name'] = translated_message.name
            if translated_message.HasField('numeric_event'):
                parsed_message['event'] = translated_message.numeric_event
            elif translated_message.HasField('boolean_event'):
                parsed_message['event'] = translated_message.boolean_event
            elif translated_message.HasField('string_event'):
                parsed_message['event'] = translated_message.string_event

            if translated_message.HasField('numeric_value'):
                parsed_message['value'] = translated_message.numeric_value
            elif translated_message.HasField('boolean_value'):
                parsed_message['value'] = translated_message.boolean_value
            elif translated_message.HasField('string_value'):
                parsed_message['value'] = translated_message.string_value
            else:
                parsed_message = None
        else:
            parsed_message = None
        return parsed_message

    def _parse_json_message(self, message_buffer):
        parsed_message = None
        remainder = message_buffer
        message = ""
        if b"\n" in message_buffer:
            message, _, remainder = message_buffer.partition(b"\n")
            try:
                parsed_message = JsonFormatter.deserialize(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                pass
        return parsed_message, remainder, len(message)

    def _parse_protobuf_message(self, message_buffer):
        parsed_message = None
        remainder = message_buffer
        message_data = ""

        # 1. decode a varint from the top of the stream
        # 2. using that as the length, if there's enough in the buffer, try and
        #       decode try and decode a VehicleMessage after the varint
        # 3. if it worked, great, we're oriented in the stream - continue
        # 4. if either couldn't be parsed, skip to the next byte and repeat
        while parsed_message is None and len(message_buffer) > 1:
            message_length, message_start = _DecodeVarint(message_buffer, 0)
            # sanity check to make sure we didn't parse some huge number that's
            # clearly not the length prefix
            if message_length > self.MAX_PROTOBUF_MESSAGE_LENGTH:
                message_buffer = message_buffer[1:]
                continue

            if message_start + message_length >= len(message_buffer):
                break

            message_data = message_buffer[message_start:message_start +
                    message_length]
            remainder = message_buffer[message_start + message_length:]

            message = openxc_pb2.VehicleMessage()
            try:
                message.ParseFromString(message_data)
            except google.protobuf.message.DecodeError as e:
                message_buffer = message_buffer[1:]
            except UnicodeDecodeError as e:
                LOG.warn("Unable to parse protobuf: %s", e)
            else:
                parsed_message = self._protobuf_to_dict(message)
                if parsed_message is None:
                    message_buffer = message_buffer[1:]

        bytes_received = 0
        if parsed_message is not None:
            bytes_received = len(message_data)
        return parsed_message, remainder, bytes_received

    def _parse_message(self, message_buffer):
        """If a message can be parsed from the given buffer, return it and
        remove it.

        Returns the message if one could be parsed, otherwise None, and the
        remainder of the buffer.
        """
        if not isinstance(message_buffer, bytes):
            message_buffer = message_buffer.encode("utf-8")

        if all((char in string.printable for char in message_buffer)):
            return self._parse_json_message(message_buffer)
        else:
            return self._parse_protobuf_message(message_buffer)

class DataSourceError(Exception):
    pass
