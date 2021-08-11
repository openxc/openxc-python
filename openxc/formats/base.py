class VehicleMessageStreamer(object):
    message_buffer = b""
    bytes_received = 0

    def receive(self, payload):
        if len(payload) > 0:
            self.message_buffer += payload
            self.bytes_received += len(payload)
