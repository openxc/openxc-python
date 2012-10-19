import threading

from openxc.formats.json import JsonFormatter


class DataSource(threading.Thread):
    def __init__(self, callback=None):
        super(DataSource, self).__init__()
        self.callback = callback
        self.daemon = True

    def read(self, num_bytes=None, timeout=None):
        raise NotImplementedError("Don't use DataSource directly")


class BytestreamDataSource(DataSource):

    def __init__(self, callback=None):
        super(BytestreamDataSource, self).__init__()
        self.bytes_received = 0

    def run(self):
        message_buffer = b""
        while True:
            message_buffer += self.read()
            while True:
                message, message_buffer, byte_count = self._parse_message(
                        message_buffer)
                if message is None:
                    break

                self.bytes_received += byte_count
                if self.callback is not None:
                    self.callback(message,
                            data_remaining=len(message_buffer) > 0)

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

class DataSourceError(Exception):
    pass
