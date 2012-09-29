from __future__ import absolute_import

import json

class JsonFormatter(object):
    @classmethod
    def deserialize(cls, message):
        return json.loads(message.decode("utf-8"))

    @classmethod
    def serialize(cls, name, value):
        return json.dumps({'name': name, 'value': value})
