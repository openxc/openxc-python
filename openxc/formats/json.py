"""JSON formatting utilities."""
from __future__ import absolute_import

import json

class JsonFormatter(object):
    SERIALIZED_COMMAND_TERMINATOR = "\x00"

    @classmethod
    def deserialize(cls, message):
        return json.loads(message.decode("utf-8"))

    @classmethod
    def serialize(cls, data):
        return json.dumps(data) + cls.SERIALIZED_COMMAND_TERMINATOR
