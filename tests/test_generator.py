from nose.tools import ok_, eq_
import unittest
import os

from openxc.generator.message_sets import JsonMessageSet
from openxc.generator.structures import BitInversionError, Signal
from openxc.generator.coder import CodeGenerator

class CodeGeneratorTests(unittest.TestCase):

    def _generate(self, filename):
        search_paths = [os.path.dirname(__file__)]
        generator = CodeGenerator(search_paths)

        message_set = JsonMessageSet.parse(
                os.path.join(os.path.dirname(__file__), filename),
                search_paths=search_paths,
            skip_disabled_mappings=True)
        ok_(message_set.validate())

        generator.message_sets.append(message_set)
        return message_set, generator.build_source()

    def _validate(self, filename):
        message_set, output = self._generate(filename)
        for signal in message_set.enabled_signals():
            ok_(signal.generic_name in output)

        for message in message_set.active_messages():
            ok_(message.name in output)
            ok_(("0x%x" % message.id) in output)

    def test_ignore_flag(self):
        message_set, output = self._generate('signals.json.example')
        for signal in message_set.enabled_signals():
            if signal.ignore:
                eq_(output.count(signal.name), 1)

    def test_non_mapped(self):
        self._validate('signals.json.example')

    def test_mapped(self):
        self._validate('mapped_signal_set.json.example')

    def test_raw_can_mode(self):
        message_set, output = self._generate('signals.json.example')
        eq_(list(message_set.valid_buses())[0].raw_can_mode, "filtered")
        eq_(list(message_set.valid_buses())[1].raw_can_mode, "off")
        eq_(output.count("passthrough"), 1)
        eq_(output.count("0x200"), 1)

    def test_max_message_frequency(self):
        message_set, output = self._generate('signals.json.example')
        eq_(list(message_set.valid_buses())[0].max_message_frequency, 5)
        eq_(list(message_set.valid_buses())[1].max_message_frequency, 0)

    def test_unfiltered_raw_can_mode(self):
        message_set, output = self._generate('mapped_signal_set.json.example')
        eq_(list(message_set.valid_buses())[0].raw_can_mode, "off")
        eq_(list(message_set.valid_buses())[1].raw_can_mode, "unfiltered")
        eq_(output.count("passthrough"), 1)

    def test_bit_inversion(self):

        eq_(Signal._invert_bit_index(24, 16), 16)
        eq_(Signal._invert_bit_index(48, 1), 55)
        eq_(Signal._invert_bit_index(8, 16), 0)

    def test_invalid_bit_inversion(self):
        try:
            Signal._invert_bit_index(0, 16)
        except BitInversionError:
            pass
        else:
            self.fail("")

    def test_max_frequency_on_message_cascades(self):
        message_set, output = self._generate('signals.json.example')
        message_with_frequency = [
                message for message in message_set.all_messages()
                if message.id == 0x121][0]
        eq_(message_with_frequency.max_signal_frequency, 10)

        signal_with_cascaded_frequency = message_with_frequency.signals['TurnSignalRight']
        eq_(signal_with_cascaded_frequency.max_frequency, 10)

        signal_with_overridden_frequency = message_with_frequency.signals['TurnSignalLeft']
        eq_(signal_with_overridden_frequency.max_frequency, 5)

    def test_default_max_frequency(self):
        message_set, output = self._generate('mapped_signal_set.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x128][0]
        eq_(message.max_frequency, 0)

    def test_max_frequency_on_set_cascades(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x128][0]
        eq_(message.max_frequency, 5)

    def test_override_max_frequency_on_bus(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x49][0]
        eq_(message.max_frequency, 2)

    def test_max_frequency_on_bus_cascades(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x200][0]
        eq_(message.max_frequency, 0)

    def test_message_frequency_in_output(self):
        message_set, output = self._generate('signals.json.example')
        message_with_frequency = [
                message for message in message_set.all_messages()
                if message.id == 0x121][0]

        found = False
        for line in output.split("\n"):
            if "CAN_BUSES" in line and message_with_frequency.name in line:
                ok_(("{%f}" % message_with_frequency.max_frequency) in line,
                        "Frequency %f should be in output: %s" %
                        (message_with_frequency.max_frequency, line))
                found = True
        ok_(found)

    def test_force_send_on_message_cascades(self):
        message_set, output = self._generate('signals.json.example')
        message = [
                message for message in message_set.all_messages()
                if message.id == 0x121][0]
        ok_(message.force_send_changed_signals)

        signal_with_overridden_flag = message.signals['TurnSignalLeft']
        ok_(not signal_with_overridden_flag.force_send_changed)

        signal_with_cascaded_flag = message.signals['TurnSignalRight']
        ok_(signal_with_cascaded_flag.force_send_changed)

    def test_default_force_send(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x128][0]
        ok_(not message.force_send_changed_signals)

    def test_force_send_in_output(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x121][0]

        found = False
        for line in output.split("\n"):
            if "CAN_BUSES" in line and message.name in line:
                # this isn't a very particular test, but it works for now
                ok_(("%s" % str(message.force_send_changed_signals).lower()) in line)
                found = True
        ok_(found)

    def test_bit_numbering_default(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x128][0]
        signal = message.signals['StrAnglErr']
        ok_(not signal.bit_numbering_inverted)
        ok_(signal.bit_position == 44)

        for message in message_set.all_messages():
            if message.id != 0x202:
                ok_(not message.bit_numbering_inverted)

    def test_bit_numbering_override(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x128][0]
        signal = message.signals['SomethingInvertedForcefully']
        ok_(signal.bit_numbering_inverted)
        ok_(signal.bit_position != 12)

    def test_bit_numbering_on_message(self):
        message_set, output = self._generate('signals.json.example')
        message = [message for message in message_set.all_messages()
                if message.id == 0x202][0]
        signal = message.signals['InvertedOnMessage']
        ok_(signal.bit_numbering_inverted)
        ok_(signal.bit_position != 12)

    def test_includes_diagnostics(self):
        message_set, output = self._generate('signals.json.example')
        ok_(len(list(message_set.all_diagnostic_messages())) > 0)
        for diagnostic_request in message_set.all_diagnostic_messages():
            ok_(diagnostic_request.generic_name in output)
