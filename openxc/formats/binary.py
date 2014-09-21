"""Binary (Protobuf) formatting utilities."""
from __future__ import absolute_import

from openxc import openxc_pb2

class BinaryFormatter(object):
    @classmethod
    def deserialize(cls, message):
        try:
            protobuf_message = openxc_pb2.VehicleMessage().ParseFromString(message,)
        except google.protobuf.message.DecodeError as e:
            pass
        except UnicodeDecodeError as e:
            LOG.warn("Unable to parse protobuf: %s", e)
        else:
            return self._protobuf_to_dict(protobuf_message)

    @classmethod
    def serialize(cls, data):
        # TODO
        return json.dumps(data) + cls.SERIALIZED_COMMAND_TERMINATOR

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
            if translated_message.HasField('event'):
                event = translated_message.event
                if event.HasField('numeric_value'):
                    parsed_message['event'] = event.numeric_value
                elif event.HasField('boolean_value'):
                    parsed_message['event'] = event.boolean_value
                elif event.HasField('string_value'):
                    parsed_message['event'] = event.string_value

            if translated_message.HasField('value'):
                value = translated_message.value
                if value.HasField('numeric_value'):
                    parsed_message['value'] = value.numeric_value
                elif value.HasField('boolean_value'):
                    parsed_message['value'] = value.boolean_value
                elif value.HasField('string_value'):
                    parsed_message['value'] = value.string_value
                else:
                    parsed_message = None
            else:
                parsed_message = None
        else:
            parsed_message = None
        return parsed_message
