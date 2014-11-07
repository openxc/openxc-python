from nose.tools import eq_, ok_

class BaseStreamerTests(object):
    def test_receive_complete(self):
        serialized_message = self.streamer.serialize_for_stream({'name': "foo", 'value': 42})
        ok_(len(serialized_message) > 1)
        self.streamer.receive(serialized_message)
        message = self.streamer.parse_next_message()
        ok_(message is not None)
        eq_(message['name'], "foo")
        eq_(message['value'], 42)

    def test_receive_partial(self):
        serialized_message = self.streamer.serialize_for_stream({'name': "foo", 'value': 42})
        self.streamer.receive(serialized_message[:-5])
        eq_(None, self.streamer.parse_next_message())
        self.streamer.receive(serialized_message[-5:])
        message = self.streamer.parse_next_message()
        ok_(message is not None)
        eq_(message['name'], "foo")
        eq_(message['value'], 42)

    def test_receive_two(self):
        serialized_messages = self.streamer.serialize_for_stream({'name': "foo", 'value': 42})
        serialized_messages += self.streamer.serialize_for_stream({'name': "bar", 'value': 24})
        self.streamer.receive(serialized_messages)
        message = self.streamer.parse_next_message()
        ok_(message is not None)
        eq_(message['name'], "foo")
        eq_(message['value'], 42)
        message = self.streamer.parse_next_message()
        ok_(message is not None)
        eq_(message['name'], "bar")
        eq_(message['value'], 24)
        eq_(None, self.streamer.parse_next_message())

    def test_serialize_command(self):
        serialized_message = self.streamer.serialize_for_stream(
                {'command': "version"})
        self.streamer.receive(serialized_message)
        message = self.streamer.parse_next_message()
        ok_(message is not None)
        eq_(message['command'], "version")

class BaseFormatterTests(object):
    """A test for every format defined in the OpenXC Message Format
    spec: https://github.com/openxc/openxc-message-format
    """

    def _check_serialized_deserialize_equal(self, deserialized):
        serialized = self.formatter.serialize(deserialized)
        eq_(deserialized, self.formatter.deserialize(serialized))

    def test_simple_vehicle_message(self):
        self._check_serialized_deserialize_equal({'name': "foo", 'value': 42})

    def test_command(self):
        self._check_serialized_deserialize_equal({'command': "version"})
        self._check_serialized_deserialize_equal({'command': "device_id"})

    def test_command_response(self):
        self._check_serialized_deserialize_equal({ "command_response":
            "version", "message": "v6.0-dev (default)", "status": True})
        self._check_serialized_deserialize_equal({ "command_response":
            "device_id", "message": "v6.0-dev (default)", "status": True})
        self._check_serialized_deserialize_equal({ "command_response":
            "passthrough", "status": False})

    def test_passthrough_command(self):
        self._check_serialized_deserialize_equal({ "command": "passthrough",
            "bus": 1,
            "enabled": True
        })

    def test_evented(self):
        self._check_serialized_deserialize_equal({"name": "button_event",
            "value": "up", "event": "pressed"})

    def test_can_message(self):
        self._check_serialized_deserialize_equal({"bus": 1, "message_id": 1234,
            "data": "0x12345678"})

    def test_diagnostic_request(self):
        self._check_serialized_deserialize_equal(
                { "command": "diagnostic_request",
                    "action": "add",
                    "request": {
                        "bus": 1,
                        "message_id": 1234,
                        "mode": 1,
                        "pid": 5,
                        "payload": "0x1234",
                        "multiple_responses": False,
                        "frequency": 1,
                        "name": "my_pid"
                    }
                })

    def test_diagnostic_response(self):
        self._check_serialized_deserialize_equal({"bus": 1,
            "message_id": 1234,
            "mode": 1,
            "pid": 5,
            "success": True,
            "payload": "0x1234",
            "value": 4660})

    def test_negative_diagnostic_response(self):
        self._check_serialized_deserialize_equal({"bus": 1,
            "message_id": 1234,
            "mode": 1,
            "success": False,
            "negative_response_code": 17})
