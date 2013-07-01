
"""
@file    openxc-python\tests\test_generator.py OpenXC Test Generator Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   OpenXC Test Generator Script."""

from nose.tools import ok_
import unittest
import os

from openxc.generator.message_sets import JsonMessageSet
from openxc.generator.coder import CodeGenerator

class CodeGeneratorTests(unittest.TestCase):
    """Code Generator Tests TestCase Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def _validate(self, filename):
        """Validate Routine"""
        search_paths = [os.path.dirname(__file__)]
        generator = CodeGenerator(search_paths)

        message_set = JsonMessageSet.parse(
                os.path.join(os.path.dirname(__file__), 
                'signals.json.example'), search_paths=search_paths,
            skip_disabled_mappings=True)
        ok_(message_set.validate())

        generator.message_sets.append(message_set)
        output = generator.build_source()

        for signal in message_set.active_signals():
            ok_(signal.generic_name in output)

        for message in message_set.active_messages():
            ok_(message.name in output)
            ok_(("0x%x" % message.id) in output)

    def test_non_mapped(self):
        """No Mapped Test Routine"""
        self._validate('signals.json.example')

    def test_mapped(self):
        """Mapped Test Routine"""
        self._validate('signals-mapped.json.example')
