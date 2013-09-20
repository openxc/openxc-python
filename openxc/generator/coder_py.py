"""
.py source code generator for the vehicle interface firmware.

-This is just a simple proof of concept implementation.
-currently just creates appropriate data structures so CAN translation can be done via python
-rather than leveraging existing python classes for json parsing and codifying their memory state after the parse,
  we are creating simple arrays of dicts to loosely match the C structs.  This gives the most flexibility
  with small Python interpreters.

-supports a single message set, needs fixed
-does not implement decode or filter, commands and handlers, these are the responsibility of the consumer of the module

"""
import os
import operator
import logging

from openxc.utils import find_file

LOG = logging.getLogger(__name__)


class CodeGeneratorPython(object):
    """This class is used to build an implementation of the signals.h functions
    from one or more CAN message sets. The message sets must already be read
    into memory and parsed.
    """

    MAX_SIGNAL_STATES = 12
    GENERATED_CODE_VERSION = "1.0"

    def __init__(self, search_paths):
        self.search_paths = search_paths
        self.message_sets = []

    def build_source(self):
        lines = []
        lines.extend(self._build_header())
        lines.extend(self._build_extra_sources())
        lines.extend(self._build_message_sets())
        lines.extend(self._build_buses())
#       lines.extend(self._build_signal_states()) #integrated into specific signal build now
        lines.extend(self._build_messages())
        #lines.extend(self._build_signals())  #done internal to build_messages now
        lines.extend(self._build_initializers())
        lines.extend(self._build_loop())
        lines.extend(self._build_commands())
#       lines.extend(self._build_decoder()) #part of footer
#       lines.extend(self._build_filters()) #part of footer
        lines.extend(self._build_footer())

        return '\n'.join(lines)

    def _build_extra_sources(self):
        lines = []
        for i, message_set in enumerate(self.sorted_message_sets):
            for extra_source_filename in message_set.extra_sources:
                with open(find_file(extra_source_filename, self.search_paths)
                        ) as extra_source_file:
                    lines.append(extra_source_file.read())
        return lines

    def _build_header(self):
        with open(os.path.join(os.path.dirname(__file__),
                'signals.py.header')) as header:
            return [header.read().format(self.GENERATED_CODE_VERSION)]

    def _build_footer(self):
        with open(os.path.join(os.path.dirname(__file__),
                'signals.py.footer')) as header:
            return [header.read().format(self.GENERATED_CODE_VERSION)]


    @property
    def sorted_message_sets(self):
        return sorted(self.message_sets, key=operator.attrgetter('name'))

    def _max_command_count(self):
        if len(self.message_sets) == 0:
            return 0

        return max(len(list(message_set.active_commands()))
                for message_set in self.message_sets)

    def _max_message_count(self):
        if len(self.message_sets) == 0:
            return 0
        return max(len(list(message_set.active_messages()))
                for message_set in self.message_sets)

    def _max_signal_count(self):
        if len(self.message_sets) == 0:
            return 0

        return max(len(list(message_set.active_signals()))
                for message_set in self.message_sets)


    def _build_messages(self):
        lines = []
        lines.append("MAX_MESSAGE_COUNT = %d" %
                self._max_message_count())
        lines.append("CAN_MESSAGES = {}")

        def block(message_set):
            lines = []
            for message_index, message in enumerate(message_set.all_messages()):
                if not message.enabled:
                    LOG.warning("Skipping disabled message %s (0x%x)" %
                            (message.name, message.id))
                    continue
                LOG.info("Added message '%s'" % message.name)
                lines.append("message = {}")
                lines.append("message['bus_index']=%d" % message_set.lookup_bus_index(message.bus_name))
                lines.append("message['id']='%03X'" % message.id)
                lines.append("message['name']='%s'" % message.name)
                lines.append("message['signals']=[]")
                
                lines.extend(self._build_signals(message))
                
                lines.append("CAN_MESSAGES['%03X'] = message" % message.id)
                lines.append("")

            return lines

        lines.extend(self._message_set_lister(block))

        lines.append("")
        return lines


    def _build_message_sets(self):
        lines = []
        lines.append("MESSAGE_SET_COUNT = %d" %
                len(self.message_sets))
        lines.append("MESSAGE_SETS = []")
        for i, message_set in enumerate(self.sorted_message_sets):
            message_set.index = i
            lines.append('set = {}')
            lines.append("set['index']=%d" % i)
            lines.append("set['name']='%s'" % message_set.name)
            lines.append("set['busCount']=%d" %  len(list(message_set.valid_buses())))
            lines.append("set['messageCount']=%d" % len(list(message_set.active_messages())))
            lines.append("set['signalCount']=%d" % len(list(message_set.active_signals())))
            lines.append("set['commandCount']=%d" % len(list(message_set.active_commands())))
            lines.append("MESSAGE_SETS.append(set)")
            lines.append("")
            LOG.info("Added message set '%s'" % message_set.name)
            return lines

    def _build_buses(self):
        lines = []
        lines.append("MAX_CAN_BUS_COUNT = 2")
        lines.append("CAN_BUSES = []")

        def block(message_set, **kwargs):
            lines = []
            for bus in message_set.valid_buses():
                lines.append('bus = {}')
                lines.append("bus['bus_speed']=%d" % bus.speed)
                lines.append("bus['address']=%d" % bus.controller)
                lines.append("CAN_BUSES.append(bus)")
                lines.append("")
            return lines

        lines.extend(self._message_set_lister(block))


        return lines


    def _build_signal_states_for_signal(self, signal):
        lines = []
        lines.append('states = []')
        for state_count, state in enumerate(signal.sorted_states):
            if state_count >= self.MAX_SIGNAL_STATES:
                LOG.warning("Ignoring anything beyond %d states for %s" % (self.MAX_SIGNAL_STATES, signal.generic_name))
                break
            lines.append("state = {}")
            lines.append("state['value']=%d" % state.value)
            lines.append("state['name']='%s'" % state.name)
            lines.append("signal['states'].append(state)")
            lines.append("")
        return lines


    def _message_set_lister(self, block, indent=4):
        lines = []
        whitespace = " " * indent
        for message_set in self.sorted_message_sets:
            lines.append(whitespace + "#message set: %s" % message_set.name)
            lines.extend(block(message_set))
        return lines

    def _message_set_switcher(self, block, indent=4):
        lines = []
        whitespace = " " * indent

        for message_set in self.sorted_message_sets:
            lines.extend(block(message_set))
        return lines


    def _build_signals(self, message):
        lines = []
        #lines.append("SIGNALS = []")

        def block(message_set):
            lines = []
            i = 1
            for signal in message.sorted_signals():
                if not signal.enabled:
                    LOG.warning("Skipping disabled signal '%s' (in 0x%x)" % (
                        signal.generic_name, signal.message.id))
                    continue
                signal.array_index = i - 1
                lines.append("signal = {}")
                lines.append("signal['message_set_index']=%d" % signal.message_set.index)
                lines.append("signal['message_index']=%d" % message_set.lookup_message_index(signal.message))
                lines.append("signal['generic_name']='%s'" % signal.generic_name)
                lines.append("signal['bit_position']=%d" % signal.bit_position)
                lines.append("signal['bit_size']=%d" % signal.bit_size)
                lines.append("signal['factor']=%f" % signal.factor)
                lines.append("signal['offset']=%f" % signal.offset)
                lines.append("signal['min_value']=%f" % signal.min_value)
                lines.append("signal['max_value']=%f" % signal.max_value)
                lines.append("signal['frequency']=%d" % signal.send_frequency)
                lines.append("signal['send_same']=%s" % signal.send_same)
                lines.append("signal['handler']=%s" % signal.handler)
                lines.append("signal['received']=False")
                lines.append("signal['sendClock']=0")
                lines.append("signal['lastValue']=0")

                if (len(signal.states) > 0):
                    lines.append("")
                    lines.append("signal['states'] = []")
                    lines.extend(self._build_signal_states_for_signal(signal))

                lines.append("signal['writable']=%s" % str(signal.writable).title())
                lines.append("signal['write_handler']=%s" % signal.write_handler or "NULL")  #handlers are implemented outside of this module for now
                lines.append("signal['name']='%s'" % signal.name)
                lines.append("message['signals'].append(signal)")
                lines.append("")

                LOG.info("Added signal '%s'" % signal.generic_name)
                i += 1
            return lines

        lines.extend(self._message_set_lister(block))
        lines.append("")

        return lines

    def _build_initializers(self):
        lines = []
        lines.append("def openxc_signals_initialize():")

        def block(message_set):
            return ["        %s()" % initializer
                for initializer in message_set.initializers]
        lines.extend(self._message_set_switcher(block))
        lines.append("")
        return lines

    def _build_loop(self):
        lines = []
        lines.append("def openxc_signals_loop():")
        def block(message_set):
            return ["        %s()" % looper for looper in message_set.loopers]
        lines.extend(self._message_set_switcher(block))
        lines.append("")
        return lines

    def _build_commands(self):
        lines = []
        lines.append("MAX_COMMAND_COUNT = %d" %
                self._max_command_count())
        lines.append("COMMANDS = []")
        def block(message_set, **kwargs):
            for command in message_set.all_commands():
                if not command.enabled:
                    LOG.warning("Skipping disabled Command %s" % command.name)
                    continue
                lines.append("command = {}")
                lines.append("command['name']='%s'" % command.name)
                lines.append("command['handler']='%s'" % command.handler)
                lines.append("COMMANDS.append(command)")
                LOG.info("Added command '%s'" % command.name)
                yield "" #        %s" % command
        lines.extend(self._message_set_lister(block))
        lines.append("")

        return lines

