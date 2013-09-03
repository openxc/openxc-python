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
                os.path.join(os.path.dirname(__file__), 'signals.json.example'),
                search_paths=search_paths,
            skip_disabled_mappings=True)
        ok_(message_set.validate())

        generator.message_sets.append(message_set)
        return message_set, generator.build_source()

    def _validate(self, filename):
        message_set, output = self._generate(filename)
        for signal in message_set.active_signals():
            ok_(signal.generic_name in output)

        for message in message_set.active_messages():
            ok_(message.name in output)
            ok_(("0x%x" % message.id) in output)

    def test_ignore_flag(self):
        message_set, output = self._generate('signals.json.example')
        for signal in message_set.active_signals():
            if signal.ignore:
                eq_(output.count(signal.name), 1)


    def test_non_mapped(self):
        self._validate('signals.json.example')

    def test_mapped(self):
        self._validate('signals-mapped.json.example')

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
