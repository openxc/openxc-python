from __future__ import absolute_import

import json

class JsonFormatter(object):
    @classmethod
    def deserialize(cls, message):
        return json.loads(message.decode("utf-8"))

    @classmethod
    def serialize(cls, name, value):
        return cls.serialize({'name': name, 'value': value})

    @classmethod
    def serialize(cls, data):
        return json.dumps(data)
