from __future__ import absolute_import

import json

class JsonSource(DataSource):
    def parse_message(self):
        if "\n" in self.message_buffer:
            message, _, remainder = self.message_buffer.partition("\n")
            try:
                parsed_message = json.loads(message)
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                if self.show_corrupted:
                    print "Corrupted: %s" % message
                if self.messages_received == 0:
                    # assume the first message will be caught mid-stream and
                    # thus will be corrupted
                    self.messages_received -= 1
            else:
                self.good_messages += 1
                if self.total_bytes_received == 0:
                    self.started_time = datetime.now()
                self.total_bytes_received += len(message)

                if self.dump:
                    print "%f: %s" % (time.time(), message)
                if self.verbose:
                    print parsed_message
                for element in self.elements:
                    if element.name == parsed_message.get('name', None):
                        element.update(parsed_message)
                        break
                return parsed_message
            finally:
                self.message_buffer = remainder
                self.messages_received += 1
            return True
        return False

    def _massage_write_value(self, value):
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

    def read(self):
        return ""

    def write(self, name, value):
        value = self._massage_write_value(value)
        message = json.dumps({'name': name, 'value': value})
        bytes_written = self._write(message + "\x00")
        assert bytes_written == len(message) + 1
