"""Contains the abstract interface for sending commands back to a vehicle
interface.
"""
import numbers
import threading

try:
    from Queue import Queue
except ImportError:
    # Python 3
    from queue import Queue

from openxc.formats.json import JsonFormatter

class CommandResponseReceiver(object):
    def __init__(self, queue, request):
        self.request = request
        self.queue = queue
        self.response = None

    def wait_for_command_response(self):
        response_received = False
        while not response_received:
            self.response = self.queue.get()
            if self.response['command_response'] == self.request['command']:
                response_received = True
            self.queue.task_done()

class Controller(object):
    """A Controller is a physical vehicle interface that accepts commands to be
    send back to the vehicle. This class is abstract, and implementations of the
    interface must define at least the ``write_bytes``, ``version``,
    ``device_id`` methods.
    """
    # TODO need to support writing protobuf

    COMMAND_RESPONSE_TIMEOUT_S = 5

    def complex_request(self, request, blocking=True):
        self.write_bytes(JsonFormatter.serialize(request))
        queue = Queue()

        self.open_requests = getattr(self, 'open_requests', [])
        self.open_requests.append(queue)

        receiver = CommandResponseReceiver(queue, request)
        t = threading.Thread(target=receiver.wait_for_command_response)
        t.daemon = True
        t.start()

        # TODO if it wasn't a blocking request, how would you get the response?
        # maybe you use non-blocking when you don't care about the response
        if blocking:
            t.join(self.COMMAND_RESPONSE_TIMEOUT_S)

        result = "Unknown"
        if receiver.response is not None:
            result = receiver.response.get('message', "Unknown")
        return result

    def version(self):
        request = {
            "command": "version"
        }
        return self.complex_request(request)

    def device_id(self):
        request = {
            "command": "device_id"
        }
        return self.complex_request(request)

    def write(self, **kwargs):
        if 'id' in kwargs and 'data' in kwargs:
            result = self.write_raw(kwargs['id'], kwargs['data'],
                    bus=kwargs.get('bus', None))
        else:
            result = self.write_translated(kwargs['name'], kwargs['value'],
                    kwargs.get('event', None))
        return result

    def write_translated(self, name, value, event):
        """Format the given signal name and value into an OpenXC write request
        and write it out to the controller interface as bytes, ending with a
        \0 character.
        """
        data = {'name': name}
        if value is not None:
            data['value'] = self._massage_write_value(value)
        if event is not None:
            data['event'] = self._massage_write_value(event);
        message = JsonFormatter.serialize(data)
        bytes_written = self.write_bytes(message)
        assert bytes_written == len(message) + 1
        return bytes_written

    def write_raw(self, message_id, data, bus=None):
        """Format the given CAN ID and data into a JSON message
        and write it out to the controller interface as bytes, ending with a
        \0 character.

        TODO this could write to a separate USB endpoint that is expecting
        raw-style JSON messages.
        """
        if not isinstance(message_id, numbers.Number):
            try:
                message_id = int(message_id, 0)
            except ValueError:
                raise ValueError("ID must be numerical")
        data = {'id': message_id, 'data': data}
        if bus is not None:
            data['bus'] = bus
        message = JsonFormatter.serialize(data)
        bytes_written = self.write_bytes(message)
        assert bytes_written == len(message) + 1
        return bytes_written

    def write_bytes(self, data):
        """Write the bytes in ``data`` out to the controller interface."""
        raise NotImplementedError("Don't use Controller directly")

    def diagnostic_request(self, request):
        """Request a diagnostic message from the vehicle interface."""
        raise NotImplementedError("%s cannot be used with control commands" %
                type(self).__name__)

    @classmethod
    def _massage_write_value(cls, value):
        """Convert string values from command-line arguments into first-order
        Python boolean and float objects, if applicable.
        """
        if not isinstance(value, numbers.Number):
            if value == "true":
                value = True
            elif value == "false":
                value = False
            elif value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
        return value


class ControllerError(Exception):
    pass
