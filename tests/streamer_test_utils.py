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

    def _check_serialized_deserialize_equal(self, deserialized):
        serialized = self.formatter.serialize(deserialized)
        eq_(deserialized, self.formatter.deserialize(serialized))

    def test_deserialize_serialized_equal(self):
        self._check_serialized_deserialize_equal({'name': "foo", 'value': 42})

    def test_deserialize_serialized_command_equal(self):
        self._check_serialized_deserialize_equal({'command': "version"})
