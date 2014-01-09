"""
C++ source code generator for the vehicle interface firmware.
"""
import os
import operator
import logging

from openxc.utils import find_file

LOG = logging.getLogger(__name__)


class CodeGenerator(object):
    """This class is used to build an implementation of the signals.h functions
    from one or more CAN message sets. The message sets must already be read
    into memory and parsed.
    """

    MAX_SIGNAL_STATES = 12
    GENERATED_CODE_VERSION = "5.x"

    def __init__(self, search_paths):
        self.search_paths = search_paths
        self.message_sets = []

    def build_source(self):
        lines = []
        lines.extend(self._build_header())
        lines.extend(self._build_extra_sources())
        lines.extend(self._build_message_sets())
        lines.extend(self._build_buses())
        lines.extend(self._build_messages())
        lines.extend(self._build_signal_states())
        lines.extend(self._build_signals())
        lines.extend(self._build_initializers())
        lines.extend(self._build_loop())
        lines.extend(self._build_commands())
        lines.extend(self._build_decoder())

        with open(os.path.join(os.path.dirname(__file__),
                'signals.cpp.footer')) as footer:
            lines.append("")
            lines.append(footer.read())

        return '\n'.join(lines)

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

        return max(len(list(message_set.enabled_signals()))
                for message_set in self.message_sets)

    def _build_header(self):
        with open(os.path.join(os.path.dirname(__file__),
                'signals.cpp.header')) as header:
            return [header.read().format(self.GENERATED_CODE_VERSION)]

    def _build_extra_sources(self):
        lines = []
        for i, message_set in enumerate(self.sorted_message_sets):
            for extra_source_filename in message_set.extra_sources:
                with open(find_file(extra_source_filename, self.search_paths)
                        ) as extra_source_file:
                    lines.append(extra_source_file.read())
        return lines

    def _build_message_set(self, index, message_set):
        LOG.info("Added message set '%s'" % message_set.name)
        return "    { %d, \"%s\", %d, %d, %d, %d }," % (index, message_set.name,
                len(list(message_set.valid_buses())),
                len(list(message_set.active_messages())),
                len(list(message_set.enabled_signals())),
                len(list(message_set.active_commands())))

    def _build_messages(self):
        lines = []
        lines.append("const int MAX_MESSAGE_COUNT = %d;" %
                self._max_message_count())
        lines.append("CanMessageDefinition CAN_MESSAGES[][MAX_MESSAGE_COUNT] = {")

        def block(message_set):
            lines = []
            for message_index, message in enumerate(message_set.all_messages()):
                if not message.active:
                    LOG.warning("Skipping disabled message %s (0x%x)" %
                            (message.name, message.id))
                    continue
                LOG.info("Added message '%s'" % message.name)
                lines.append("        %s" % message)
            return lines

        lines.extend(self._message_set_lister(block))

        lines.append("};")
        lines.append("")
        return lines

    def _build_message_sets(self):
        lines = []
        lines.append("const int MESSAGE_SET_COUNT = %d;" %
                len(self.message_sets))
        lines.append("CanMessageSet MESSAGE_SETS[MESSAGE_SET_COUNT] = {")
        for i, message_set in enumerate(self.sorted_message_sets):
            message_set.index = i
            lines.append(self._build_message_set(i, message_set))
        lines.append("};")
        lines.append("")
        return lines

    def _build_buses(self):
        lines = []
        lines.append("const int MAX_CAN_BUS_COUNT = 2;")
        lines.append("CanBus CAN_BUSES[][MAX_CAN_BUS_COUNT] = {")

        def block(message_set, **kwargs):
            lines = []
            for bus in message_set.valid_buses():
                lines.append(str(bus))
                lines.append("")
            return lines

        lines.extend(self._message_set_lister(block))
        lines.append("};")
        lines.append("")

        return lines

    def _build_signal_states(self):
        lines = []
        lines.append("const int MAX_SIGNAL_STATES = %d;" %
                self.MAX_SIGNAL_STATES)
        lines.append("const int MAX_SIGNAL_COUNT = %d;" %
                self._max_signal_count())
        lines.append("const CanSignalState SIGNAL_STATES[]"
                "[MAX_SIGNAL_COUNT][MAX_SIGNAL_STATES] = {")

        def block(message_set, **kwargs):
            states_index = 0
            lines = []
            for signal in message_set.enabled_signals():
                if len(signal.states) > 0:
                    line = "        { "
                    for state_count, state in enumerate(signal.sorted_states):
                        if state_count >= self.MAX_SIGNAL_STATES:
                            LOG.warning("Ignoring anything beyond %d states for %s" %
                                    (self.MAX_SIGNAL_STATES,
                                        signal.generic_name))
                            break
                        line += "%s, " % state
                    line += "},"
                    lines.append(line)
                    signal.states_index = states_index
                    states_index += 1
            return lines

        lines.extend(self._message_set_lister(block))

        lines.append("};")
        lines.append("")

        return lines

    def _message_set_lister(self, block, indent=4):
        lines = []
        whitespace = " " * indent
        for message_set in self.sorted_message_sets:
            lines.append(whitespace + "{ // message set: %s" % message_set.name)
            lines.extend(block(message_set))
            lines.append(whitespace + "},")
        return lines

    def _message_set_switcher(self, block, indent=4):
        lines = []
        whitespace = " " * indent
        lines.append(whitespace + "switch(getConfiguration()"
                "->messageSetIndex) {")
        for message_set in self.sorted_message_sets:
            lines.append(whitespace + "case %d: // message set: %s" % (
                    message_set.index, message_set.name))
            lines.extend(block(message_set))
            lines.append(whitespace * 2 + "break;")
            lines.append(whitespace + "}")
        return lines

    def _build_signals(self):
        lines = []
        lines.append("CanSignal SIGNALS[][MAX_SIGNAL_COUNT] = {")

        def block(message_set):
            lines = []
            i = 1
            for signal in message_set.all_signals():
                if not signal.enabled:
                    LOG.warning("Skipping disabled signal '%s' (in 0x%x)" % (
                        signal.generic_name, signal.message.id))
                    continue
                signal.array_index = i - 1
                lines.append("        %s" % signal)
                LOG.info("Added signal '%s'" % signal.generic_name)
                i += 1
            return lines

        lines.extend(self._message_set_lister(block))
        lines.append("};")
        lines.append("")

        return lines

    def _build_initializers(self):
        lines = []
        lines.append("void openxc::signals::initialize() {")

        def block(message_set):
            return ["        %s();" % initializer
                for initializer in message_set.initializers]
        lines.extend(self._message_set_switcher(block))
        lines.append("}")
        lines.append("")
        return lines

    def _build_loop(self):
        lines = []
        lines.append("void openxc::signals::loop() {")
        def block(message_set):
            return ["        %s();" % looper for looper in message_set.loopers]
        lines.extend(self._message_set_switcher(block))
        lines.append("}")
        lines.append("")
        return lines

    def _build_commands(self):
        lines = []
        lines.append("const int MAX_COMMAND_COUNT = %d;" %
                self._max_command_count())
        lines.append("CanCommand COMMANDS[][MAX_COMMAND_COUNT] = {")
        def block(message_set, **kwargs):
            for command in message_set.all_commands():
                if not command.enabled:
                    LOG.warning("Skipping disabled Command %s" % command.name)
                    continue
                LOG.info("Added command '%s'" % command.name)
                yield "        %s" % command
        lines.extend(self._message_set_lister(block))
        lines.append("};")
        lines.append("")

        return lines

    def _build_decoder(self):
        lines = []
        lines.append("void openxc::signals::decodeCanMessage("
                "Pipeline* pipeline, CanBus* bus, int id, uint64_t data) {")

        def block(message_set):
            lines = []
            lines.append(" " * 8 + "switch(bus->address) {")
            for bus in message_set.valid_buses():
                lines.append(" " * 8 + "case %s:" % bus.controller)
                lines.append(" " * 12 + "switch (id) {")
                for message in bus.active_messages():
                    if (len(list(message.active_signals())) > 0 or
                            len(list(message.handlers)) > 0):
                        lines.append(" " * 12 + "case 0x%x: // %s" % (message.id,
                                message.name))
                        for handler in message.handlers:
                            lines.append(" " * 16 + "%s(id, data, SIGNALS[%d], " % (
                                handler, message_set.index) +
                                    "getSignalCount(), pipeline);")
                        for signal in message.active_signals():
                            line = " " * 16
                            line += ("can::read::translateSignal(pipeline, "
                                        "&SIGNALS[%d][%d], data, " %
                                        (message_set.index, signal.array_index))
                            if signal.handler:
                                line += "&%s, " % signal.handler
                            line += ("SIGNALS[%d], getSignalCount()); // %s" % (
                                message_set.index, signal.name))
                            lines.append(line)
                        lines.append("                break;")
                lines.append("            }")
                if bus.raw_can_mode != "off":
                    lines.append(" " * 12 + "openxc::can::read::passthroughMessage("
                            "bus, id, data, getMessages(), getMessageCount(), pipeline);")
                lines.append("            break;")
            lines.append("        }")
            return lines

        lines.extend(self._message_set_switcher(block))

        lines.append("}")
        lines.append("")

        return lines
