"""Binary (Protobuf) formatting utilities."""
from __future__ import absolute_import

import binascii
import numbers

import google.protobuf.message
from google.protobuf.internal.decoder import _DecodeVarint
from google.protobuf.internal import encoder

from openxc.formats.base import VehicleMessageStreamer
from openxc import openxc_pb2

class BinaryStreamer(VehicleMessageStreamer):
    MAX_PROTOBUF_MESSAGE_LENGTH = 200

    def parse_next_message(self):
        message = None
        remainder = self.message_buffer
        message_data = ""

        # 1. decode a varint from the top of the stream
        # 2. using that as the length, if there's enough in the buffer, try and
        #       decode try and decode a VehicleMessage after the varint
        # 3. if it worked, great, we're oriented in the stream - continue
        # 4. if either couldn't be parsed, skip to the next byte and repeat
        while message is None and len(self.message_buffer) > 1:
            message_length, message_start = _DecodeVarint(self.message_buffer, 0)
            # sanity check to make sure we didn't parse some huge number that's
            # clearly not the length prefix
            if message_length > self.MAX_PROTOBUF_MESSAGE_LENGTH:
                self.message_buffer = self.message_buffer[1:]
                continue

            if message_start + message_length > len(self.message_buffer):
                break

            message_data = self.message_buffer[message_start:message_start +
                    message_length]
            remainder = self.message_buffer[message_start + message_length:]

            message = BinaryFormatter.deserialize(message_data)
            if message is None:
                self.message_buffer = self.message_buffer[1:]

        self.message_buffer = remainder
        return message

    def serialize_for_stream(self, message):
        protobuf_message = BinaryFormatter.serialize(message)
        delimiter = encoder._VarintBytes(len(protobuf_message))
        return delimiter + protobuf_message


class BinaryFormatter(object):
    @classmethod
    def deserialize(cls, data):
        message = openxc_pb2.VehicleMessage()
        try:
            message.ParseFromString(data)
        except google.protobuf.message.DecodeError as e:
            pass
        except UnicodeDecodeError as e:
            LOG.warn("Unable to parse protobuf: %s", e)
        else:
            return cls._protobuf_to_dict(message)

    @classmethod
    def serialize(cls, data):
        return cls._dict_to_protobuf(data).SerializeToString()

    @classmethod
    def _dict_to_protobuf(cls, data):
        message = openxc_pb2.VehicleMessage()
        if 'command' in data:
            command_name = data['command']
            message.type = openxc_pb2.VehicleMessage.CONTROL_COMMAND
            if command_name == "version":
                message.control_command.type = openxc_pb2.ControlCommand.VERSION
            elif command_name == "device_id":
                message.control_command.type = openxc_pb2.ControlCommand.DEVICE_ID
            elif command_name == "diagnostic_request":
                message.control_command.type = openxc_pb2.ControlCommand.DIAGNOSTIC
                # TODO
            elif command_name == "passthrough":
                message.control_command.type = openxc_pb2.ControlCommand.PASSTHROUGH
                message.control_command.passthrough_mode_request.bus = data['bus']
                message.control_command.passthrough_mode_request.enabled = data['enabled']
        elif 'name' in data and 'value' in data:
            message.type = openxc_pb2.VehicleMessage.TRANSLATED
            message.translated_message.name = data['name']
            value = data['value']
            if isinstance(value, bool):
                message.translated_message.type = openxc_pb2.TranslatedMessage.BOOL
                message.translated_message.value.boolean_value = value
            elif isinstance(value, str):
                message.translated_message.type = openxc_pb2.TranslatedMessage.STRING
                message.translated_message.value.string_value = value
            elif isinstance(value, numbers.Number):
                message.translated_message.type = openxc_pb2.TranslatedMessage.NUM
                message.translated_message.value.numeric_value = value
            # TODO handle evented simple vehicle messages, too

        else:
            # TODO
            pass
        return message

    @classmethod
    def _protobuf_to_dict(cls, message):
        parsed_message = {}
        if message is not None:
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
            elif message.type == message.CONTROL_COMMAND:
                command = message.control_command
                if command.type == openxc_pb2.ControlCommand.VERSION:
                    parsed_message['command'] = "version"
                elif command.type == openxc_pb2.ControlCommand.DEVICE_ID:
                    parsed_message['command'] = "device_id"
                elif command.type == openxc_pb2.ControlCommand.DIAGNOSTIC:
                    parsed_message['command'] = "diagnostic_request"
                elif command.type == openxc_pb2.ControlCommand.PASSTHROUGH:
                    parsed_message['command'] = "passthrough"
                # TODO the rest of the fields
            else:
                parsed_message = None
        return parsed_message
