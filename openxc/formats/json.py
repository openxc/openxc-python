"""JSON formatting utilities."""
from __future__ import absolute_import

import json

from openxc.formats.base import VehicleMessageStreamer

class JsonStreamer(VehicleMessageStreamer):
    SERIALIZED_COMMAND_TERMINATOR = b"\x00"

    def parse_next_message(self):
        parsed_message = None
        remainder = self.message_buffer
        message = ""
        if self.SERIALIZED_COMMAND_TERMINATOR in self.message_buffer:
            message, _, remainder = self.message_buffer.partition(
                    self.SERIALIZED_COMMAND_TERMINATOR)
            try:
                parsed_message = JsonFormatter.deserialize(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                pass
        self.message_buffer = remainder
        return parsed_message

    def serialize_for_stream(self, message):
        return JsonFormatter.serialize(
                message) + self.SERIALIZED_COMMAND_TERMINATOR

class JsonFormatter(object):

    @classmethod
    def deserialize(cls, message):
        return json.loads(message.decode("utf8"))

    @classmethod
    def serialize(cls, data):
        return json.dumps(data).encode("utf8")
