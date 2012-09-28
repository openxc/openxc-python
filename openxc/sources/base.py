import threading

from openxc.formats.json import JsonFormatter


class DataSource(object):
    def __init__(self, callback):
        self.messages_received = 0
        self.good_messages = 0
        self.total_bytes_received = 0
        self.callback = callback

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        message_buffer = ""
        while True:
            message_buffer += self.read()
            while True:
                message, message_buffer, received = self._parse_message(
                        message_buffer)
                if received and message is None and self.messages_received == 0:
                    # assume the first message will be caught mid-stream and
                    # thus will be corrupted
                    self.messages_received -= 1
                else:
                    self.good_messages += 1
                    self.total_bytes_received += len(message)
                    self.callback(message)

                if received:
                    self.messages_received += 1

    def read(self, num_bytes=None, timeout=None):
        raise NotImplementedError("Don't use DataSource directly")

    def write_bytes(self, data):
        raise NotImplementedError("Don't use DataSource directly")

    def write(self, name, value):
        value = self._massage_write_value(value)
        message = JsonFormatter.serialize(name, value)
        bytes_written = self.write_bytes(message + "\x00")
        assert bytes_written == len(message) + 1

    @classmethod
    def _massage_write_value(cls, value):
        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            try:
                value = float(value)
            except ValueError:
                pass
        return value

    def _parse_message(self, message_buffer):
        """If a message can be pasred from the given buffer, return it and
        remove it.

        Returns the message if one could be parsed, otherwise None, and the
        remainder of the buffer.
        """
        parsed_message = None
        received = False
        remainder = message_buffer
        if "\n" in message_buffer:
            received = True
            message, _, remainder = message_buffer.partition("\n")
            try:
                parsed_message = JsonFormatter.deserialize(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                pass
        return parsed_message, remainder, received
