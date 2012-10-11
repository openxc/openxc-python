import threading

from openxc.formats.json import JsonFormatter


class DataSource(object):
    def __init__(self, callback=None):
        self.callback = callback
        self.bytes_received = 0

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        try:
            while self.thread.is_alive():
                self.thread.join(5)
        except (KeyboardInterrupt, SystemExit):
            return

    def run(self):
        message_buffer = b""
        while True:
            message_buffer += self.read()
            while True:
                message, message_buffer, byte_count = self._parse_message(
                        message_buffer)
                if message is not None:
                    self.bytes_received += byte_count
                    if self.callback is not None:
                        self.callback(message)
                else:
                    break

    def read(self, num_bytes=None, timeout=None):
        raise NotImplementedError("Don't use DataSource directly")

    def write_bytes(self, data):
        raise NotImplementedError("Don't use DataSource directly")

    def version(self):
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    def reset(self):
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    def write(self, name, value):
        value = self._massage_write_value(value)
        message = JsonFormatter.serialize({'name': name, 'value': value})
        bytes_written = self.write_bytes(message + "\x00")
        assert bytes_written == len(message) + 1
        return bytes_written

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

class DataSourceError(Exception): pass
