import operator
import math
from collections import defaultdict

import logging

LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, name=None, handler=None, enabled=True, **kwargs):
        self.name = name
        self.handler = handler
        self.enabled = enabled

    def __str__(self):
        return "{ \"%s\", %s }," % (self.name, self.handler)


class Message(object):
    def __init__(self, bus_name=None, id=None, name=None,
            bit_numbering_inverted=None, handlers=None, enabled=True):
        self.bus_name = bus_name
        self.id = id
        self.name = name
        self.bit_numbering_inverted = bit_numbering_inverted
        self.handlers = handlers or []
        self.enabled = enabled
        self.signals = defaultdict(Signal)

    @property
    def id(self):
        return getattr(self, '_id', None)

    @id.setter
    def id(self, value):
        if value is not None:
            if not isinstance(value, int):
                value = int(value, 0)
            self._id = value

    def merge_message(self, data):
        self.bus_name = self.bus_name or data.get('bus', None)
        self.id = self.id or data.get('id')
        self.name = self.name or data.get('name', None)
        self.bit_numbering_inverted = (self.bit_numbering_inverted or
                data.get('bit_numbering_inverted', None))
        self.handlers.extend(data.get('handlers', []))
        # Support deprecated single 'handler' field
        if 'handler' in data:
            self.handlers.append(data.get('handler'))
        if self.enabled is None:
            self.enabled = data.get('enabled', True)
        else:
            self.enabled = data.get('enabled', self.enabled)

        if 'signals' in data:
            self.merge_signals(data['signals'])

    def merge_signals(self, data):
        for signal_name, signal_data in data.items():
            states = []
            for name, raw_matches in signal_data.get('states', {}).items():
                for raw_match in raw_matches:
                    states.append(SignalState(raw_match, name))
            signal_data.pop('states', None)

            signal = self.signals[signal_name]
            signal.name = signal_name
            signal.message_set = self.message_set
            signal.message = self
            # TODO this will clobber existing states but I don't have a really
            # obvious clean solution to it at the moment
            signal.states = states
            signal.merge_signal(signal_data)

    def validate(self):
        if self.bus_name is None:
            LOG.warning("No default or explicit bus for message %s" % self.id)
            return False

        if self.bus_name not in self.message_set.buses:
            LOG.warning("Bus '%s' (from message 0x%x) is not defined" %
                    (self.bus_name, self.id))
            return False
        return True

    def sorted_signals(self):
        for signal in sorted(self.signals.values(),
                key=operator.attrgetter('generic_name')):
            yield signal


    def to_dict(self):
        return {"name": self.name,
                "signals": dict((key, value.to_dict())
                    for key, value in self.signals.items())}

    def __str__(self):
        bus_index = self.message_set.lookup_bus_index(self.bus_name)
        if bus_index is not None:
            return "{&CAN_BUSES[%d][%d], 0x%x}, // %s" % (
                    self.message_set.index, bus_index, self.id, self.name)
        else:
            LOG.warning("Bus address '%s' is invalid, only %s are allowed - message 0x%x will be disabled\n" %
                    (self.bus_name, CanBus.VALID_BUS_ADDRESSES, self.id))
        return ""

class CanBus(object):
    # Only works with 2 CAN buses since we are limited by 2 CAN controllers,
    # and we want to be a little careful that we always expect 0x101 to be
    # plugged into the CAN1 controller and 0x102 into CAN2.
    VALID_BUS_ADDRESSES = (1, 2)

    def __init__(self, name=None, speed=None, controller=None, **kwargs):
        self.name = name
        self.speed = speed
        self.messages = defaultdict(Message)
        self.controller = controller

    def valid(self):
        return self.controller in self.VALID_BUS_ADDRESSES

    def active_messages(self):
        for message in self.sorted_messages():
            if message.enabled:
                yield message

    def sorted_messages(self):
        for message in sorted(self.messages.values(),
                key=operator.attrgetter('id')):
            yield message

    def get_or_create_message(self, message_id):
        return self.messages[message_id]

    def add_message(self, message):
        self.messages.append(message)

    def __str__(self):
        result = """        {{ {bus_speed}, {controller}, can{controller},
            #ifdef __PIC32__
            handleCan{controller}Interrupt,
            #endif // __PIC32__
        }},"""
        return result.format(bus_speed=self.speed, controller=self.controller)


class Signal(object):
    def __init__(self, message_set=None, message=None, states=None, **kwargs):
        self.message_set = message_set
        self.message = message

        self.name = None
        self.generic_name = None
        self.bit_position = None
        self.bit_size = None
        self.handler = None
        self.write_handler = None
        self.factor = 1
        self.offset = 0
        self.min_value = 0.0
        self.max_value = 0.0
        self.send_frequency = 1
        self.send_same = True
        self.writable=False
        self.enabled = True
        self.ignore = False
        self.states = states or []

        self.merge_signal(kwargs)

    def merge_signal(self, data):
        self.name = data.get('name', self.name)
        self.enabled = data.get('enabled', self.enabled)
        self.generic_name = data.get('generic_name', self.generic_name)
        self.bit_position = data.get('bit_position', self.bit_position)
        self.bit_size = data.get('bit_size', self.bit_size)
        self.factor = data.get('factor', self.factor)
        self.offset = data.get('offset', self.offset)
        self.min_value = data.get('min_value', self.min_value)
        self.max_value = data.get('max_value', self.max_value)
        self.handler = data.get('handler', self.handler)
        self.writable = data.get('writable', self.writable)
        self.write_handler = data.get('write_handler', self.write_handler)
        self.send_same = data.get('send_same', self.send_same)
        self.ignore = data.get('ignore', self.ignore)
        # the frequency determines how often the message should be propagated. a
        # frequency of 1 means that every time the signal it is received we will
        # try to handle it. a frequency of 2 means that every other signal
        # will be handled (and the other half is ignored). This is useful for
        # trimming down the data rate of the stream over USB.
        self.send_frequency = data.get('send_frequency', self.send_frequency)

    @property
    def handler(self):
        handler = getattr(self, '_handler', None)
        if handler is None:
            if self.ignore:
                handler = "ignoreHandler"
            if len(self.states) > 0:
                handler = "stateHandler"
        return handler

    @handler.setter
    def handler(self, value):
        self._handler = value

    @property
    def enabled(self):
        signal_enabled = getattr(self, '_enabled', True)
        if self.message is not None:
            return self.message.enabled and signal_enabled
        return signal_enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = value

    @property
    def sorted_states(self):
        return sorted(self.states, key=operator.attrgetter('value'))

    def to_dict(self):
        return {"generic_name": self.generic_name,
                "bit_position": self.bit_position,
                "bit_size": self.bit_size,
                "factor": self.factor,
                "offset": self.offset,
                "min_value": self.min_value,
                "max_value": self.max_value}

    def translate(self, can_data):
        translated_value = int(can_data, 16)

        # Trim off everything to the right
        translated_value >>= 64 - self.bit_position - self.bit_size
        mask = int(math.pow(2, self.bit_size)) - 1
        translated_value &= mask
        translated_value *= self.factor
        translated_value += self.offset
        return translated_value

    def validate(self):
        if self.send_same is False and self.send_frequency != 1:
            LOG.warning("Signal %s combines send_same and " % self.generic_name +
                    "send_frequency - this is not recommended")
        if self.bit_position == None or self.bit_size == None:
            LOG.warning("%s (generic name: %s) is incomplete\n" %
                    (self.name, self.generic_name))
            return False
        return True

    @property
    def bit_position(self):
        if getattr(self, '_bit_position', None) is not None and getattr(
                self.message, 'bit_numbering_inverted', False):
            return self._invert_bit_index(self._bit_position, self.bit_size)
        else:
            return self._bit_position

    @bit_position.setter
    def bit_position(self, value):
        self._bit_position = value

    @classmethod
    def _invert_bit_index(cls, i, l):
        (b, r) = divmod(i, 8)
        end = (8 * b) + (7 - r)
        return(end - l + 1)

    def __str__(self):
        result =  ("{&CAN_MESSAGES[%d][%d], \"%s\", %s, %d, %f, %f, %f, %f, "
                    "%d, %s, false, " % (
                self.message_set.index,
                self.message_set.lookup_message_index(self.message),
                self.generic_name, self.bit_position, self.bit_size,
                self.factor, self.offset, self.min_value, self.max_value,
                self.send_frequency, str(self.send_same).lower()))
        if len(self.states) > 0:
            result += "SIGNAL_STATES[%d][%d], %d" % (self.message_set.index,
                    self.states_index, len(self.states))
        else:
            result += "NULL, 0"
        result += ", %s, %s" % (str(self.writable).lower(),
                self.write_handler or "NULL")
        result += "}, // %s" % self.name
        return result


class SignalState(object):
    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __str__(self):
        return "{%d, \"%s\"}" % (self.value, self.name)
