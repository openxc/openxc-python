class VehicleMessageStreamer(object):
    message_buffer = b""
    bytes_received = 0

    def receive(self, payload):
        if not isinstance(payload, bytes):
            payload = payload.encode("utf-8")
        self.message_buffer += payload
        self.bytes_received += len(payload)
