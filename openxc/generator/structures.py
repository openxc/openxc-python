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


class DiagnosticMessage(object):
    def __init__(self, message_set, enabled=True, **kwargs):
        self.message_set = message_set
        self.enabled = enabled
        self.id = kwargs['id']
        self.bus = kwargs['bus']
        self.generic_name = kwargs.get('generic_name', None)
        self.parse_payload = kwargs.get('parse_payload', False)
        self.factor = kwargs.get('factor', None)
        self.offset = kwargs.get('offset', None)
        self.handler = kwargs.get('handler', None)
        self.mode = kwargs['mode']
        self.pid = kwargs.get('pid', 0)
        self.pid_length = kwargs.get('pid_length', 0)
        self.frequency = kwargs.get('frequency', 0)

    def __str__(self):
        result = "{\n        DiagnosticRequest request = {arbitration_id: 0x%x, mode: 0x%x, has_pid: %s, pid: 0x%x, pid_length: %d};\n" % (
                self.id, self.mode, str(self.pid > 0).lower(), self.pid,
                self.pid_length)

        if self.generic_name or self.handler or self.factor or self.offset or self.parse_payload:
            if self.generic_name:
                name = "\"%s\"" % self.generic_name
            else:
                name = "NULL"

            if self.factor is not None:
                factor = self.factor
            else:
                factor = 1.0

            if self.offset is not None:
                offset = self.offset
            else:
                offset = 0


            result += "        addDiagnosticRequest(diagnosticsManager, &getCanBuses()[%d], &request, %s, %f, %f, %s, %d);\n        }\n" % (
                    self.message_set.lookup_bus_index(self.bus),
                    name,
                    factor,
                    offset,
                    self.handler or "NULL",
                    self.frequency)
        else:
            result += "        addDiagnosticRequest(diagnosticsManager, &getCanBuses()[%d], &request, %d);\n        }\n" % (
                    self.message_set.lookup_bus_index(self.bus), self.frequency)
        return result


class Message(object):
    def __init__(self, bus_name=None, id=None, name=None,
            bit_numbering_inverted=None, handlers=None, enabled=True):
        self.bus_name = bus_name
        self.id = id
        self.name = name
        self.bit_numbering_inverted = bit_numbering_inverted
        self.handlers = handlers or []
        self.enabled = enabled
        self.max_frequency = None
        self.max_signal_frequency = 0
        self.force_send_changed = True
        self.force_send_changed_signals = False
        self.signals = defaultdict(Signal)

    @property
    def active(self):
        return self.enabled and (len(list(self.enabled_signals())) > 0
                or len(self.handlers) > 0)

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

        if getattr(self, 'message_set'):
            self.bus = self.message_set.lookup_bus(self.bus_name)
            if not self.bus.valid():
                self.enabled = False
                msg = ""
                if self.bus is None:
                    msg = "Bus '%s' is invalid, only %s are defined" % (
                            self.bus_name, list(self.message_set.valid_buses()))
                else:
                    msg = "Bus '%s' is disabled" % self.bus_name
                LOG.warning("%s - message 0x%x will be disabled" % (msg, self.id))

        self.id = self.id or data.get('id')
        self.name = self.name or data.get('name', None)
        self.bit_numbering_inverted = (self.bit_numbering_inverted or
                data.get('bit_numbering_inverted', None))

        self.max_frequency = data.get('max_frequency', self.max_frequency)
        if self.max_frequency is None:
            self.max_frequency = self.bus.max_message_frequency

        self.max_signal_frequency = data.get('max_signal_frequency',
                self.max_signal_frequency)
        self.force_send_changed = data.get('force_send_changed',
                self.force_send_changed)
        self.force_send_changed_signals = data.get('force_send_changed_signals',
                self.force_send_changed_signals)
        self.handlers.extend(data.get('handlers', []))
        if 'handler' in data:
            # Support deprecated single 'handler' field
            self.handlers.append(data.get('handler'))
            LOG.warning("The 'handler' attribute on the message " +
                    "%s is deprecated but will still work for " % self.name +
                    "now - the replacement is a 'handlers' array")
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
        for signal in sorted(self.enabled_signals(),
                key=operator.attrgetter('generic_name')):
            yield signal

    def enabled_signals(self):
        for signal in self.signals.values():
            if signal.enabled:
                yield signal

    def active_signals(self):
        """An active signal is one that's enabled and not ignored, i.e. it
        should be translated.
        """
        for signal in self.sorted_signals():
            if not signal.ignore:
                yield signal

    def to_dict(self):
        return {"name": self.name,
                "signals": dict((key, value.to_dict())
                    for key, value in self.signals.items())}

    def __str__(self):
        bus_index = self.message_set.lookup_bus_index(self.bus_name)
        if bus_index is not None:
            return "{&CAN_BUSES[%d][%d], 0x%x, {%d}, %s}, // %s" % (
                    self.message_set.index, bus_index, self.id,
                    self.max_frequency,
                    str(self.force_send_changed).lower(),
                    self.name)
        else:
            bus = self.message_set.lookup_bus(self.bus_name)
            msg = ""
            if bus is None:
                msg = "Bus '%s' is invalid, only %s are defined" % (
                        self.bus_name, list(self.message_set.valid_buses()))
            else:
                msg = "Bus '%s' is disabled" % self.bus_name
            LOG.warning("%s - message 0x%x will be disabled\n" % (msg, self.id))
        return ""

class CanBus(object):
    # Only works with 2 CAN buses since we are limited by 2 CAN controllers,
    # and we want to be a little careful that we always expect 0x101 to be
    # plugged into the CAN1 controller and 0x102 into CAN2.
    VALID_BUS_ADDRESSES = (1, 2)

    def __init__(self, name=None, speed=None, controller=None,
            default_max_message_frequency=None,
            max_message_frequency=None,
            default_raw_can_mode=None,
            raw_can_mode=None,
            raw_writable=False,
            **kwargs):
        self.name = name
        self.speed = speed
        self.messages = defaultdict(Message)
        self.controller = controller
        self.max_message_frequency = max_message_frequency
        if self.max_message_frequency is None:
            self.max_message_frequency = default_max_message_frequency
        self.raw_can_mode = raw_can_mode or default_raw_can_mode
        self.raw_writable = raw_writable

    def valid(self):
        return self.controller in self.VALID_BUS_ADDRESSES

    def active_messages(self):
        for message in self.sorted_messages():
            if message.active:
                yield message

    def enabled_signals(self):
        for message in self.active_messages():
            for signal in message.enabled_signals():
                yield signal

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
            {max_message_frequency}, {raw_writable},
            #ifdef __PIC32__
            handleCan{controller}Interrupt,
            #endif // __PIC32__
        }},"""
        return result.format(bus_speed=self.speed, controller=self.controller,
                max_message_frequency=self.max_message_frequency,
                raw_writable=str(self.raw_writable).lower())


class BitInversionError(Exception):
    pass


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
        self.max_frequency = None
        self.send_same = True
        self.force_send_changed = None
        self.writable = False
        self.enabled = True
        self.ignore = False
        self.bit_numbering_inverted = None
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
        # Kind of nasty, but we want to avoid actually setting one of the
        # implicit handlers on the object (and then later on, assuming that it
        # was set explicitly)
        self.handler = data.get('handler', getattr(self, '_handler', None))
        self.writable = data.get('writable', self.writable)
        self.write_handler = data.get('write_handler', self.write_handler)
        self.send_same = data.get('send_same', self.send_same)
        self.force_send_changed = data.get('force_send_changed',
                self.force_send_changed)
        self.ignore = data.get('ignore', self.ignore)
        self.max_frequency = data.get('max_frequency', self.max_frequency)
        self.bit_numbering_inverted = data.get('bit_numbering_inverted')

        if 'send_frequency' in data:
            LOG.warning("The 'send_frequency' attribute in the signal " +
                    "%s is deprecated and has no effect " % self.generic_name +
                    " - see the replacement, max_frequency")

    @property
    def handler(self):
        handler = getattr(self, '_handler', None)
        if handler is None:
            if self.ignore:
                handler = "ignoreHandler"
            elif len(self.states) > 0:
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
    def max_frequency(self):
        max_freq = getattr(self, '_max_frequency', None)
        if max_freq is None and self.message is not None:
            max_freq = self.message.max_signal_frequency
        return max_freq

    @max_frequency.setter
    def max_frequency(self, value):
        self._max_frequency = value

    @property
    def force_send_changed(self):
        force_send = getattr(self, '_force_send_changed', None)
        if force_send is None and self.message is not None:
            force_send = self.message.force_send_changed_signals
        return force_send

    @force_send_changed.setter
    def force_send_changed(self, value):
        self._force_send_changed = value

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
        if self.send_same is False and self.max_frequency > 0:
            LOG.warning("Signal %s combines send_same and " % self.generic_name +
                    "max_frequency - this is not recommended")
        if self.bit_position == None or self.bit_size == None:
            LOG.error("%s (generic name: %s) is incomplete\n" %
                    (self.name, self.generic_name))
            return False
        return True

    @property
    def bit_position(self):
        if (getattr(self, '_bit_position', None) is not None and
                self.bit_numbering_inverted):
            return self._invert_bit_index(self._bit_position, self.bit_size)
        else:
            return self._bit_position

    @bit_position.setter
    def bit_position(self, value):
        self._bit_position = value

    @property
    def bit_numbering_inverted(self):
        if getattr(self, '_bit_numbering_inverted', None) is None:
            return getattr(self.message, 'bit_numbering_inverted', False)
        return self._bit_numbering_inverted

    @bit_numbering_inverted.setter
    def bit_numbering_inverted(self, value):
        if value != None:
            self._bit_numbering_inverted = value

    @classmethod
    def _invert_bit_index(cls, bit_index, length):
        (b, r) = divmod(bit_index, 8)
        end = (8 * b) + (7 - r)
        inverted_index = end - length + 1
        if inverted_index < 0:
            raise BitInversionError("Bit index %d with length %d cannot be " %
                        (bit_index, length) +
                    "inverted - you probably need to disable the "
                    "'bit_numbering_inverted' flag in your JSON mapping")
        return inverted_index

    def __str__(self):
        result =  ("{&CAN_MESSAGES[%d][%d], \"%s\", %s, %d, %f, %f, %f, %f, "
                    "{%d}, %s, %s, " % (
                self.message_set.index,
                self.message_set.lookup_message_index(self.message),
                self.generic_name, self.bit_position, self.bit_size,
                self.factor, self.offset, self.min_value, self.max_value,
                self.max_frequency, str(self.send_same).lower(),
                str(self.force_send_changed).lower()))
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
