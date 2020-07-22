"""Contains the abstract interface for sending commands back to a vehicle
interface.
"""
import numbers
import time
import threading
import binascii

try:
    from queue import Queue
    from queue import Empty
except ImportError:
    # Python 3
    from queue import Queue
    from queue import Empty

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

    COMMAND_RESPONSE_TIMEOUT_S = 0.5

    def __init__(self, queue, request, quit_after_first=True):
        """Construct a new ResponseReceiver.

        queue - A multithreading queue that this receiver will pull potential responses from.
        request - The request we are trying to match up with a response.
        """
        self.diag_dict = {}
        self.request = request
        self.queue = queue
        self.responses = []
        self.running = True
        self.quit_after_first = quit_after_first

    def _response_matches_request(self, response):
        """Inspect the given response and return true if it's a response to this
        ResponseReceiver's request.

        This implementation is the base class no-op - it returns True for any
        response. You probably want to override this in a subclass.

        response - the response to inspect.
        """
        return True

    def wait_for_responses(self):
        """Block the thread and wait for the response to the given request to
        arrive from the VI. If no matching response is received in
        COMMAND_RESPONSE_TIMEOUT_S seconds, returns anyway.
        """

        self.thread.join(self.COMMAND_RESPONSE_TIMEOUT_S)
        self.running = False

        return self.responses

    def start(self):
        self.thread = threading.Thread(target=self.handle_responses)
        self.thread.start()

    def handle_responses(self):
        """Block and wait for responses to this object's original request, or
        until a timeout (self.COMMAND_RESPONSE_TIMEOUT_S).

        This function is handy to use as the target function for a thread.

        The responses received (or None if none was received before the timeout)
        is stored in a list at self.responses.
        """
        while self.running:
            try:
                response = self.queue.get(
                        timeout=self.COMMAND_RESPONSE_TIMEOUT_S)
                if self._response_matches_request(response):
                    if type(self) == DiagnosticResponseReceiver:
                        if self._response_is_multiframe(response):
                            if response['id'] in self.diag_dict:
                                self.diag_dict[response['id']].addFrame(response)
                            else:
                                self.diag_dict[response['id']] = MultiframeDiagnosticMessage(response)
                            if self._return_final(response):
                                self.responses.append(self.diag_dict[response['id']].getResponse())
                                self.diag_dict.pop(response['id'])
                    self.responses.append(response)
                    if self.quit_after_first:
                        self.running = False
                self.queue.task_done()
            except Empty:
                break
                
class MultiframeDiagnosticMessage:
    def __init__(self, response):
        self.id = response['id'] - 16
        self.mode = response['mode']
        self.bus = response['bus']
        self.pid = response['pid']
        self.payload = '0x' + response['payload'][8:]
        
    def addFrame(self, response):
        self.payload += response['payload'][8:]
        
    def getResponse(self):
        request = {
            'timestamp': 0,
            'bus': self.bus,
            'id': self.id,
            'mode': self.mode,
            'success': True,
            'pid': self.pid,
            'payload': self.payload
        }
        return request

class CommandResponseReceiver(ResponseReceiver):
    """A receiver that matches the 'command' field in responses to the
    original request.
    """

    def _response_matches_request(self, response):
        """Return true if the 'command' field in the response matches the
        original request.
        """
        return response.get('command_response', None) == self.request['command']

class DiagnosticResponseReceiver(ResponseReceiver):
    """A receiver that matches the bus, ID, mode and PID from a
    diagnostic request to an incoming response.
    """
    
    def __init__(self, queue, request):
        super(DiagnosticResponseReceiver, self).__init__(queue, request,
                quit_after_first=False)
        # Make sure to key off of the diagnostic request, not the command to
        # create the request
        self.diagnostic_request = request['request']

    def _response_matches_request(self, response):
        """Return true if the response is to a diagnostic request, and the bus,
        id, mode match. If the request was successful, the PID echo is also
        checked.
        """
        # Accept success/failure command responses
        if super(DiagnosticResponseReceiver,
                self)._response_matches_request(response):
            return True

        if ('bus' in self.diagnostic_request and
                response.get('bus', None) != self.diagnostic_request['bus']):
            return False
        if (self.diagnostic_request['id'] != 0x7df and
                response.get('id', None) != self.diagnostic_request['id']):
            return False

        if (response.get('success', True) and
                response.get('pid', None) !=
                    self.diagnostic_request.get('pid', None)):
            return False

        return response.get('mode', None) == self.diagnostic_request['mode']
        
    def _response_is_multiframe(self, response):
        if 'frame' in response:
            return True
        return False
        
    def _return_final(self, response):
        if response['frame'] == -1:
            return True
        return False

class Controller(object):
    """A Controller is a physical vehicle interface that accepts commands to be
    send back to the vehicle. This class is abstract, and implementations of the
    interface must define at least the ``write_bytes`` method.
    """

    def _prepare_response_receiver(self, request,
            receiver_class=CommandResponseReceiver):
        queue = Queue()

        self.open_requests = getattr(self, 'open_requests', [])
        self.open_requests.append(queue)

        receiver = receiver_class(queue, request)
        receiver.start()
        # Give it a brief moment to get started so we make sure get the response
        time.sleep(.2)
        return receiver

    def complex_request(self, request, wait_for_first_response=True):
        """Send a compound command request to the interface over the normal data
        channel.

        request - A dict storing the request to send to the VI. It will be
            serialized to the currently selected output format.
        wait_for_first_response - If true, this function will block waiting for
            a response from the VI and return it to the caller. Otherwise, it
            will send the command and return immediately and any response will
            be lost.
        """
        receiver = self._prepare_response_receiver(request,
                receiver_class=CommandResponseReceiver)
        self._send_complex_request(request)

        responses = []
        if wait_for_first_response:
            responses = receiver.wait_for_responses()
        return responses
        
    def _send_complex_request(self, request):
        self.write_bytes(self.streamer.serialize_for_stream(request))

    @classmethod
    def _build_diagnostic_request(cls, id, mode, bus=None, pid=None,
            frequency=None, payload=None, decoded_type=None):
        request = {
            'command': "diagnostic_request",
            'request': {
                'id': id,
                'mode': mode
            }
        }

        if bus is not None:
            request['request']['bus'] = bus
            request['request']['mode'] = mode
        if payload is not None and len(payload) > 0:
            # payload must be a bytearray
            request['request']['payload'] = "0x%s" % binascii.hexlify(payload)
        if pid is not None:
            request['request']['pid'] = pid
        if frequency is not None:
            request['request']['frequency'] = frequency
        if decoded_type is not None:
            request['request']['decoded_type'] = decoded_type

        return request

    def delete_diagnostic_request(self, id, mode, bus=None, pid=None):
        request = self._build_diagnostic_request(id, mode, bus, pid)
        request['action'] = 'cancel'
        return self._check_command_response_status(request)

    def create_diagnostic_request(self, id, mode, bus=None, pid=None,
            frequency=None, payload=None, wait_for_ack=True,
            wait_for_first_response=False, decoded_type=None):
        """Send a new diagnostic message request to the VI

        Required:

        id - The message ID (arbitration ID) for the request.
        mode - the diagnostic mode (or service).

        Optional:

        bus - The address of the CAN bus controller to send the request, either
            1 or 2 for current VI hardware.
        pid - The parameter ID, or PID, for the request (e.g. for a mode 1
            request).
        frequency - The frequency in hertz to add this as a recurring diagnostic
            requests. Must be greater than 0, or None if it is a one-time
            request.
        payload - A bytearray to send as the request's optional payload. Only
            single frame diagnostic requests are supported by the VI firmware in
            the current version, so the payload has a maximum length of 6.
        wait_for_ack - If True, will wait for an ACK of the command message.
        wait_for_first_response - If True, this function will block waiting for
            a diagnostic response to be received for the request. It will return
            either after timing out or after 1 matching response is received -
            there may be more responses to functional broadcast requests that
            arrive after returning.

        Returns a tuple of
            ([list of ACK responses to create request],
                [list of diagnostic responses received])

        """

        request = self._build_diagnostic_request(id, mode, bus, pid,
                frequency, payload, decoded_type)

        diag_response_receiver = None
        if wait_for_first_response:
            diag_response_receiver = self._prepare_response_receiver(
                    request, DiagnosticResponseReceiver)

        request['action'] = 'add'
        ack_responses = self.complex_request(request, wait_for_ack)

        diag_responses = None
        if diag_response_receiver is not None:
            diag_responses = diag_response_receiver.wait_for_responses()

        return ack_responses, diag_responses

    def _check_command_response_status(self, request):
        responses = self.complex_request(request)
        return len(responses) > 0 and responses[0]['status']

    def set_passthrough(self, bus, enabled):
        """Control the status of CAN message passthrough for a bus.

        Returns True if the command was successful.
        """
        request = {
            "command": "passthrough",
            "bus": bus,
            "enabled": enabled
        }
        return self._check_command_response_status(request)

    def set_payload_format(self, payload_format):
        """Set the payload format for messages sent to and from the VI.

        Returns True if the command was successful.
        """
        request = {
            "command": "payload_format",
            "format": payload_format
        }
        status = self._check_command_response_status(request)
        # Always change the format regardless because if it was already in the
        # right format, the command will have failed.
        self.format = payload_format
        return status

		
    def rtc_configuration(self, unix_time):
        """Set the Unix time if RTC is supported on the device.

        Returns True if the command was successful.
        """
        request = {
            "command": "rtc_configuration",
            "unix_time": unix_time
        }
        status = self._check_command_response_status(request)
        return status
		
    def modem_configuration(self, host, port):
        """Set the host:port for the Cellular device to send data to.

        Returns True if the command was successful.
        """
        request = {
            "command": "modem_configuration",
            "host": host,
            "port": port
        }
        status = self._check_command_response_status(request)
        return status

    def set_acceptance_filter_bypass(self, bus, bypass):
        """Control the status of CAN acceptance filter for a bus.

        Returns True if the command was successful.
        """
        request = {
            "command": "af_bypass",
            "bus": bus,
            "bypass": bypass
        }
        return self._check_command_response_status(request)

    def set_predefined_obd2_requests(self, enabled):
        """Control if pre-defined OBD2 requests should be sent.

        Returns True if the command was successful.
        """
        request = {
            "command": "predefined_obd2",
            "enabled": enabled
        }
        return self._check_command_response_status(request)

    def _check_command_response_message(self, request):
        responses = self.complex_request(request)
        result = None
        if len(responses) > 0:
            result = responses[0].get('message')
        return result

    def version(self):
        """Request a firmware version identifier from the VI.
        """
        request = {
            "command": "version"
        }
        return self._check_command_response_message(request)
        
    def platform(self):
        """Request the VI platform.
        """
        request = {
            "command": "platform"
        }
        return self._check_command_response_message(request)

    def sd_mount_status(self):
        """Request for SD Mount status if available.
        """
        request = {
            "command": "sd_mount_status"
        }
        responses = self.complex_request(request)
        result = None
        if len(responses) > 0:
            result = responses[0].get('status')
        return result
		
    def device_id(self):
        """Request the unique device ID of the attached VI.
        """
        request = {
            "command": "device_id"
        }
        return self._check_command_response_message(request)

    def write(self, **kwargs):
        """Serialize a raw or translated write request and send it to the VI,
        following the OpenXC message format.
        """
        if 'id' in kwargs and 'data' in kwargs:
            result = self.write_raw(kwargs['id'], kwargs['data'],
                    bus=kwargs.get('bus', None),
                    frame_format=kwargs.get('frame_format', None))
        else:
            result = self.write_translated(kwargs['name'], kwargs['value'],
                    event=kwargs.get('event', None))
        return result

    def write_translated(self, name, value, event=None):
        """Send a translated write request to the VI.
        """
        data = {'name': name}
        if value is not None:
            data['value'] = self._massage_write_value(value)
        if event is not None:
            data['event'] = self._massage_write_value(event);
        message = self.streamer.serialize_for_stream(data)
        bytes_written = self.write_bytes(message)
        assert bytes_written == len(message)
        return bytes_written

    def write_raw(self, id, data, bus=None, frame_format=None):
        """Send a raw write request to the VI.
        """
        if not isinstance(id, numbers.Number):
            try:
                id = int(id, 0)
            except ValueError:
                raise ValueError("ID must be numerical")
        data = {'id': id, 'data': data}
        if bus is not None:
            data['bus'] = bus
        if frame_format is not None:
            data['frame_format'] = frame_format
        message = self.streamer.serialize_for_stream(data)
        bytes_written = self.write_bytes(message)
        assert bytes_written == len(message)
        return bytes_written

    def stop(self):
        pass

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
