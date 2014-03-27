"""Contains the abstract interface for sending commands back to a vehicle
interface.
"""
import numbers
import threading
import binascii

try:
    from Queue import Queue
    from Queue import Empty
except ImportError:
    # Python 3
    from queue import Queue
    from queue import Empty

from openxc.formats.json import JsonFormatter

class ResponseReceiver(object):
    """All commands to a vehicle interface are asynchronous. This class is used to
    wait for the response for a particular request in a thread. Before making a
    request, a ResponseReceiver is created to wait for the response. All
    responses received from the VI (which may or may not be in response to this
    particular command) are passed to the ResponseReceiver, until it either
    times out waiting or finds a matching response.

    The synchronization mechanism is a multiprocessing Queue. The
    ResponseReceiver blocks waiting on a new response to be added to the queue,
    and the vehicle interface class puts newly received responses in the queues
    of ResponseReceivers as they arrive.
    """
    def __init__(self, queue, request):
        """Construct a new ResponseReceiver.

        queue - A multithreading queue that this receiver will pull potential responses from.
        request - The request we are trying to match up with a response.
        """
        self.request = request
        self.queue = queue
        self.response = None

    def _response_matches_request(self, response):
        """Inspect the given response and return true if it's a response to this
        ResponseReceiver's request.

        This implementation is the base class no-op - it returns True for any
        response. You probably want to override this in a subclass.

        response - the response to inspect.
        """
        return True

    def wait_for_command_response(self):
        """Block and wait for a response to this object's original request, or
        until a timeout (Controller.COMMAND_RESPONSE_TIMEOUT_S).

        This function is handy to use as the target function for a thread.

        The response received (or None if none was received before the timeout)
        is stored at self.response and also returned from this function.
        """
        response_received = False
        while not response_received:
            try:
                self.response = self.queue.get(
                        timeout=Controller.COMMAND_RESPONSE_TIMEOUT_S)
                if self._response_matches_request(self.response):
                    response_received = True
                self.queue.task_done()
            except Empty:
                break
        return self.response

class CommandResponseReceiver(ResponseReceiver):
    """A receiver that matches the 'command' field in responses to the
    original request.
    """

    def _response_matches_request(self, response):
        """Return true if the 'command' field in the response matches the
        original request.
        """
        return self.response.get(
                'command_response', None) == self.request['command']

class DiagnosticResponseReceiver(ResponseReceiver):
    """A receiver that matches the bus, ID, mode and PID from a
    diagnostic request to an incoming response.
    """

    def __init__(self, queue, request):
        super(DiagnosticResponseReceiver, self).__init__(queue, request)
        self.diagnostic_request = request['request']

    def _response_matches_request(self, response):
        """Return true if the response is to a diagnostic request, and the bus,
        id, mode match. If the request was successful, the PID echo is also
        checked.
        """
        if ('bus' in self.diagnostic_request and
                response.get('bus', None) != self.diagnostic_request['bus']):
            return False
        if (self.diagnostic_request['id'] != 0x7df and
                response.get('id', None) == self.diagnostic_request['id']):
            return False

        if (response.get('success', True) and
                response.get('pid', None) !=
                    self.diagnostic_request.get('pid', None)):
            return False

        return response.get('mode', None) == self.diagnostic_request['mode']


class Controller(object):
    """A Controller is a physical vehicle interface that accepts commands to be
    send back to the vehicle. This class is abstract, and implementations of the
    interface must define at least the ``write_bytes`` method.
    """

    COMMAND_RESPONSE_TIMEOUT_S = .11

    def _wait_for_response(self, request):
        """Block the thread and wait for the response to the given request to
        arrive from the VI. If no matching response is received in
        COMMAND_RESPONSE_TIMEOUT_S seconds, returns anyway.
        """

        queue = Queue()

        self.open_requests = getattr(self, 'open_requests', [])
        self.open_requests.append(queue)

        if request['command'] == "diagnostic_request":
            receiver = DiagnosticResponseReceiver(queue, request)
        else:
            receiver = CommandResponseReceiver(queue, request)

        t = threading.Thread(target=receiver.wait_for_command_response)
        t.start()
        t.join(self.COMMAND_RESPONSE_TIMEOUT_S)

        return receiver.response

    def complex_request(self, request, wait_for_first_response=True):
        """Send a compound command request to the interface over the normal data
        channel.

        request - A dict storing the request to send to the VI. It will be
            serialized to JSON, as that is the only supported format for
            commands on the VI in the current firmware.
        wait_for_first_response - If true, this function will block waiting for
            a response from the VI and return it to the caller. Otherwise, it
            will send the command and return immediately and any response will
            be lost.
        """
        self.write_bytes(JsonFormatter.serialize(request))

        result = None
        if wait_for_first_response:
            response = self._wait_for_response(request)
            if response is not None:
                result = response.get('message', "Unknown")
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
            # payload must be a bytearray
            request['request']['payload'] = "0x%s" % binascii.hexlify(payload)
        if pid is not None:
            request['request']['pid'] = pid
        if frequency is not None:
            request['request']['frequency'] = frequency

        return request

    def diagnostic_request(self, message_id, mode, bus=None, pid=None,
            frequency=None, payload=None, wait_for_first_response=False):
        """Send a new diagnostic message request to the VI

        Required:

        message_id - The message ID (arbitration ID) for the request.
        mode - the diagnostic mode (or service).

        Optional:

        bus - The address of the CAN bus controller to send the request, either
            1 or 2 for current VI hardware.
        pid - The parameter ID, or PID, for the request (e.g. for a mode 1
            request).
        frequency - The frequency in hertz to add this as a recurring diagnostic
            requests. If None or 0, it will be a one-time request.
        payload - A bytearray to send as the request's optional payload. Only
            single frame diagnostic requests are supported by the VI firmware in
            the current version, so the payload has a maximum length of 6.
        wait_for_first_response - If True, this function will block waiting for
            a response to be received for the request. It will return either
            after timing out or after 1 matching response is received - there
            may be more responses to functional broadcast requests that arrive
            after returning.

        """

        request = self._build_diagnostic_request(message_id, mode, bus, pid,
                frequency, payload)
        return self.complex_request(request, wait_for_first_response)

    def version(self):
        """Request a firmware version identifier from the VI.
        """
        request = {
            "command": "version"
        }
        return self.complex_request(request)

    def device_id(self):
        """Request the unique device ID of the attached VI.
        """
        request = {
            "command": "device_id"
        }
        return self.complex_request(request)

    def write(self, **kwargs):
        """Serialize a raw or translated write request as JSON and send it to
        the VI, following the OpenXC message format.
        """
        if 'id' in kwargs and 'data' in kwargs:
            result = self.write_raw(kwargs['id'], kwargs['data'],
                    bus=kwargs.get('bus', None))
        else:
            result = self.write_translated(kwargs['name'], kwargs['value'],
                    kwargs.get('event', None))
        return result

    def write_translated(self, name, value, event):
        """Send a translated write request to the VI.
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
        """Send a raw write request to the VI.
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
        """Write the bytes in ``data`` to the controller interface."""
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
