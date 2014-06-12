from nose.tools import ok_, eq_
import unittest
import os

from openxc.generator.message_sets import JsonMessageSet
from openxc.generator.structures import BitInversionError, Signal
from openxc.generator.coder import CodeGenerator

class DiagnosticCodeGeneratorTests(unittest.TestCase):

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
        for request in message_set.active_diagnostic_messages():
            ok_(("0x%x" % request.id) in output)
            if request.decoder is not None:
                ok_(request.decoder in output)

    def test_includes_decoder(self):
        self._validate('diagnostic.json.example')

    def test_includes_diagnostics(self):
        message_set, output = self._generate('signals.json.example')
        ok_(len(list(message_set.all_diagnostic_messages())) > 0)
        for diagnostic_request in message_set.all_diagnostic_messages():
            ok_(diagnostic_request.name in output)
