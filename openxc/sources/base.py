import threading

from openxc.formats.json import JsonFormatter


class DataSource(object):
    def __init__(self):
        self.messages_received = 0
        self.good_messages = 0
        self.total_bytes_received = 0
        self.message_buffer = ""

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            self.message_buffer += self.read()
            while self._parse_message():
                continue

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

    def _parse_message(self):
        if "\n" in self.message_buffer:
            message, _, remainder = self.message_buffer.partition("\n")
            try:
                parsed_message = JsonFormatter.deserialize(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                if self.messages_received == 0:
                    # assume the first message will be caught mid-stream and
                    # thus will be corrupted
                    self.messages_received -= 1
            else:
                self.good_messages += 1
                self.total_bytes_received += len(message)

                return parsed_message
            finally:
                self.message_buffer = remainder
                self.messages_received += 1
            return True
        return False
