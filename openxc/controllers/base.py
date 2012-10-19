from openxc.formats.json import JsonFormatter


class Controller(object):
    def write(self, name, value):
        value = self._massage_write_value(value)
        message = JsonFormatter.serialize({'name': name, 'value': value})
        bytes_written = self.write_bytes(message + "\x00")
        assert bytes_written == len(message) + 1
        return bytes_written

    def write_bytes(self, data):
        raise NotImplementedError("Don't use Controller directly")

    def version(self):
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    def reset(self):
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

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

class ControllerError(Exception):
    pass
