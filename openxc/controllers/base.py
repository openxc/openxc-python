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

class ResponseReceiver(object):
    def __init__(self, queue, request):
        self.request = request
        self.queue = queue
        self.response = None

    def wait_for_command_response(self):
        response_received = False
        while not response_received:
            self.response = self.queue.get()
            if self._response_matches_request(self.response):
                response_received = True
            self.queue.task_done()

class CommandResponseReceiver(object):
    def _response_matches_request(self, response):
        return self.response['command_response'] == self.request['command']

class DiagnosticResponseReceiver(ResponseReceiver):
    def _response_matches_request(self, response):
        # TODO need to handle negative responses, which may not include the PID
        # echo
        return (response.get('bus') == self.request.bus and
                response.get('id') == self.request.id and
                response.get('mode') == self.request.mode and
                response.get('pid', None) == self.request.pid)

class Controller(object):
    """A Controller is a physical vehicle interface that accepts commands to be
    send back to the vehicle. This class is abstract, and implementations of the
    interface must define at least the ``write_bytes`` method.
    """

    COMMAND_RESPONSE_TIMEOUT_S = .2

    def _wait_for_response(self, request):
        queue = Queue()

        self.open_requests = getattr(self, 'open_requests', [])
        self.open_requests.append(queue)

        if request['command'] == "diagnostic_request":
            receiver = DiagnosticResponseReceiver(queue, request)
        else:
            receiver = CommandResponseReceiver(queue, request)

        t = threading.Thread(target=receiver.wait_for_command_response)
        t.daemon = True
        t.start()
        t.join(self.COMMAND_RESPONSE_TIMEOUT_S)

        return receiver

    def complex_request(self, request, wait_for_first_response=True):
        """Send a compound command request to the interface over the normal data
        channel.

        request - A dict storing the request to send to the VI. It will be
            encoded as JSON currently, as that is the only supported format for
            commands.
        wait_for_first_response - If true, this function will block waiting for a
            response from the VI and return it to the caller. Otherwise, it will
            send the command and return immediately and any response will be
            lost.

        Only JSON formatted commands are supported right now.
        """
        self.write_bytes(JsonFormatter.serialize(request))

        result = None
        if wait_for_first_response:
            receiver = self._wait_for_response(request)
            if receiver.response is not None:
                result = receiver.response.get('message', "Unknown")
        return result

    @classmethod
    def _build_diagnostic_request(cls, message_id, mode, bus=None, pid=None,
            frequency=None, payload=None):
        request = {
            'command': "diagnostic_request",
            'request': {
                'id': message_id
            }
        }

        if bus is not None:
            request['request']['bus'] = bus
        if mode is not None:
            request['request']['mode'] = mode
        if payload is not None:
            # TODO what format is the payload going to be? hex?
            request['request']['payload'] = payload
        if pid is not None:
            request['request']['pid'] = pid
        if frequency is not None:
            request['request']['frequency'] = frequnecy

        return request

    def diagnostic_request(self, message_id, mode, bus=None, pid=None,
            frequency=None, payload=None, wait_for_first_response=False):
        # TODO currently this is going to exit after the first response.
        # what about broadcast requests? we may just need to stay alive for
        # 1 second
        request = self._build_diagnostic_request(message_id, mode, bus, pid,
                frequency, payload)
        self.complex_request(request, wait_for_first_response)

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
        assert bytes_written == len(message)
        return bytes_written

    def write_raw(self, message_id, data, bus=None):
        """Format the given CAN ID and data into a JSON message
        and write it out to the controller interface as bytes, ending with a
        \0 character.
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
        assert bytes_written == len(message)
        return bytes_written

    def write_bytes(self, data):
        """Write the bytes in ``data`` out to the controller interface."""
        raise NotImplementedError("Don't use Controller directly")

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
