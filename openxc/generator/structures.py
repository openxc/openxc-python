import operator
import math
from collections import defaultdict
from openxc.utils import fatal_error

import logging

LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, name=None, handler=None, enabled=True, **kwargs):
        self.name = name
        self.handler = handler
        self.enabled = enabled

    def __str__(self):
        return "{ genericName: \"%s\", handler: %s }," % (self.name, self.handler)


class DiagnosticMessage(object):
    def __init__(self, message_set, enabled=True, **kwargs):
        self.message_set = message_set
        self.enabled = enabled
        self.id = kwargs['id']

        self.bus_name = kwargs['bus']
        if not isinstance(self.bus_name, str):
            raise ConfigurationError("Bus name must be name of bus in "
                    "config, was '%s'" % self.bus_name)

        self.bus = self.message_set.lookup_bus_index(self.bus_name)
        if self.bus is None:
            raise ConfigurationError("Unable to find bus with name '%s'"
                    % self.bus_name)

        self.name = kwargs.get('name', None)
        self.multiple_responses = kwargs.get('multiple_responses', False)
        self.decoder = kwargs.get('decoder', None)
        self.callback = kwargs.get('callback', None)
        self.mode = kwargs['mode']
        self.pid = kwargs.get('pid', 0)
        self.pid_length = kwargs.get('pid_length', 0)

        try:
            self.frequency = kwargs['frequency']
        except KeyError:
            raise ConfigurationError("Frequency must be specified for "
                "pre-configured diagnostic request (bus: "
                "%s, id: %d, mode: %d, pid: %d" % (self.bus_name,
                        self.id, self.mode, self.pid))

    def __str__(self):
        result = "{\n        DiagnosticRequest request = {arbitration_id: 0x%x, mode: 0x%x, has_pid: %s, pid: 0x%x, pid_length: %d};\n" % (
                self.id, self.mode, str(self.pid > 0).lower(), self.pid,
                self.pid_length)

        if self.name:
            name = "\"%s\"" % self.name
        else:
            name = "NULL"

        result += " " * 8 + "addRecurringRequest(diagnosticsManager, &getCanBuses()[%d], &request, %s, %s, %s, %s, %f);\n        }\n" % (
                self.message_set.lookup_bus_index(self.bus_name),
                name,
                str(self.multiple_responses).lower(),
                self.decoder or "NULL",
                self.callback or "NULL",
                self.frequency)
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
        return self.enabled

    @property
    def id(self):
        return getattr(self, '_id', None)

    @id.setter
    def id(self, value):
        if value is not None:
            if not isinstance(value, int):
                value = int(value, 0)
            self._id = value

    def validate_bus(self):
        if getattr(self, 'message_set'):
            self.bus = self.message_set.lookup_bus(name=self.bus_name)
            if not self.bus.valid():
                self.enabled = False
                msg = ""
                if self.bus is None:
                    msg = "Bus '%s' is invalid, only %s are defined" % (
                            self.bus_name, list(self.message_set.valid_buses()))
                else:
                    msg = "Bus '%s' is disabled" % self.bus_name
                LOG.warning("%s - message 0x%x will be disabled" % (msg, self.id))

    def merge_message(self, data):
        self.bus_name = self.bus_name or data.get('bus', None)

        message_attributes = dir(self)
        message_attributes = [a.replace('bus_name', 'bus') for a in message_attributes]
        data_attributes = list(data.keys())
        extra_attributes = set(data_attributes) - set(message_attributes)

        if extra_attributes:
            fatal_error('ERROR: Message %s has unrecognized attributes: %s' % (data.get('id'), ', '.join(extra_attributes)))

        self.validate_bus()

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
        for signal_name, signal_data in list(data.items()):
            states = []
            for name, raw_matches in list(signal_data.get('states', {}).items()):
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
        for signal in list(self.signals.values()):
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
                    for key, value in list(self.signals.items()))}

    def __str__(self):
        bus_index = self.message_set.lookup_bus_index(self.bus_name)
        if bus_index is not None:
            id_format = "STANDARD";
            if self.id > 2047:
                id_format = "EXTENDED";
            return "{ bus: &CAN_BUSES[%d][%d], id: 0x%x, format: %s, frequencyClock: {%f}, forceSendChanged: %s}, // %s" % (
                    self.message_set.index, bus_index, self.id,
                    id_format,
                    self.max_frequency,
                    str(self.force_send_changed).lower(),
                    self.name)
        else:
            bus = self.message_set.lookup_bus(name=self.bus_name)
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
            loopback=False,
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
        self.loopback = loopback

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
        for message in sorted(list(self.messages.values()),
                key=operator.attrgetter('id')):
            yield message

    def get_or_create_message(self, message_id):
        return self.messages[message_id]

    def add_message(self, message):
        self.messages.append(message)

    @property
    def passthrough(self):
        return self.raw_can_mode != "off"

    @property
    def bypass_filters(self):
        return self.raw_can_mode == "unfiltered"

    def __str__(self):
        result = """        {{ speed: {bus_speed},
        address: {controller},
        maxMessageFrequency: {max_message_frequency},
        rawWritable: {raw_writable},
        passthroughCanMessages: {passthrough},
        bypassFilters: {bypass_filters},
        loopback: {loopback}
        }},"""
        return result.format(bus_speed=self.speed, controller=self.controller,
                max_message_frequency=self.max_message_frequency,
                raw_writable=str(self.raw_writable).lower(),
                passthrough=str(self.passthrough).lower(),
                bypass_filters=str(self.bypass_filters).lower(),
                loopback=str(self.loopback).lower())


class ConfigurationError(Exception):
    pass

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
        self.decoder = None
        self.encoder = None
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
        self.generic_name = data.get('generic_name', self.name)
        self.bit_position = data.get('bit_position', self.bit_position)
        self.bit_size = data.get('bit_size', self.bit_size)
        self.factor = data.get('factor', self.factor)
        self.offset = data.get('offset', self.offset)
        self.min_value = data.get('min_value', self.min_value)
        self.max_value = data.get('max_value', self.max_value)
        # Kind of nasty, but we want to avoid actually setting one of the
        # implicit handlers on the object (and then later on, assuming that it
        # was set explicitly)
        self.decoder = data.get('decoder', getattr(self, '_decoder', None))
        self.writable = data.get('writable', self.writable)
        self.encoder = data.get('encoder', self.encoder)
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

        signal_attributes = dir(self)
        data_attributes = list(data.keys())
        extra_attributes = set(data_attributes) - set(signal_attributes)

        if extra_attributes:
           fatal_error('ERROR: Signal %s in %s has unrecognized attributes: %s' % (self.name, self.message.name, ', '.join(extra_attributes)))
        

    @property
    def decoder(self):
        decoder = getattr(self, '_decoder', None)
        if decoder is None:
            if self.ignore:
                decoder = "ignoreDecoder"
            elif len(self.states) > 0:
                decoder = "stateDecoder"
        return decoder

    @decoder.setter
    def decoder(self, value):
        self._decoder = value

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
        result =  ("{message: &CAN_MESSAGES[%d][%d], genericName: \"%s\", bitPosition: %s, bitSize: %d, factor: %f, offset: %f, minValue: %f, maxValue: %f, frequency: %f, sendSame: %s, forceSendChanged: %s, " % (
                self.message_set.index,
                self.message_set.lookup_message_index(self.message),
                self.generic_name, self.bit_position, self.bit_size,
                self.factor, self.offset, self.min_value, self.max_value,
                self.max_frequency, str(self.send_same).lower(),
                str(self.force_send_changed).lower()))
        if len(self.states) > 0:
            result += "states: SIGNAL_STATES[%d][%d], stateCount: %d" % (self.message_set.index,
                    self.states_index, len(self.states))
        else:
            result += "states: NULL, stateCount: 0"
        result += ", writable: %s, decoder: %s, encoder: %s" % (str(self.writable).lower(),
                self.decoder or "NULL",
                self.encoder or "NULL")
        result += "}, // %s" % self.name
        return result


class SignalState(object):
    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __str__(self):
        return "{value: %d, name: \"%s\"}" % (self.value, self.name)
