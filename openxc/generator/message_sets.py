"""
This modules contains the logic to parse and validate JSON files in the OpenXC
message set format.
"""

from __future__ import print_function
from collections import defaultdict
import operator
import logging

from .xml_to_json import merge_database_into_mapping
from .structures import Command, CanBus
from openxc.utils import fatal_error, merge, find_file, \
        load_json_from_search_path

LOG = logging.getLogger(__name__)


class MessageSet(object):
    """Message Set Class"""
    def __init__(self, name):
        """Initialization Routine"""
        self.name = name
        self.buses = defaultdict(CanBus)
        self.initializers = []
        self.loopers = []
        self.commands = []
        self.extra_sources = set()

    def valid_buses(self):
        """Valid Buses"""
        valid_buses = [bus for bus in self.buses.values() if bus.valid()]
        return sorted(valid_buses, key=operator.attrgetter('controller'))

    def active_messages(self):
        """Active Messages Routine"""
        for message in self.all_messages():
            if message.enabled:
                yield message

    def all_messages(self):
        """All Messages Routine"""
        for bus in self.valid_buses():
            for message in bus.sorted_messages():
                yield message

    def active_signals(self):
        """Active Signals Routine"""
        for signal in self.all_signals():
            if signal.enabled:
                yield signal

    def active_commands(self):
        """Active Commands Routine"""
        for command in self.all_commands():
            if command.enabled:
                yield command

    def all_commands(self):
        """All Commands Routine"""
        for command in sorted(self.commands, key=operator.attrgetter('name')):
            yield command

    def all_signals(self):
        """All Signals Routine"""
        for message in self.all_messages():
            for signal in message.sorted_signals():
                yield signal

    def validate(self):
        """Validate Routine"""
        return self.validate_name() and self.validate_messages()

    def validate_messages(self):
        """Validate Messages Routine"""
        valid = True
        for message in self.all_messages():
            valid = valid and message.validate()
        for signal in self.all_signals():
            valid = valid and signal.validate()
        return valid

    def validate_name(self):
        """Validate Name Routine"""
        if self.name is None:
            LOG.warning("missing message set (%s)" % self.name)
            return False
        return True

    def lookup_message_index(self, message):
        """Lookup Message Index Routine"""
        for i, candidate in enumerate(self.active_messages()):
            if candidate.id == message.id:
                return i

    def lookup_bus_index(self, bus_name):
        """Lookup Bus Index Routine"""
        bus = self.buses.get(bus_name, None)
        if bus and bus.controller is not None:
            for index, candidate_bus_address in enumerate(CanBus.VALID_BUS_ADDRESSES):
                if candidate_bus_address == bus.controller:
                    return index
        return None

    def _message_count(self):
        """Message Count Routine"""
        return len(list(self.all_messages()))


class JsonMessageSet(MessageSet):
    """Json Message Set Class"""
    
    @classmethod
    def parse(cls, filename, search_paths=None, skip_disabled_mappings=False):
        """Parse Routine"""
        search_paths = search_paths or []

        data = load_json_from_search_path(filename, search_paths)

        # Flatten all parent files into one dict
        while len(data.get('parents', [])) > 0:
            for parent_filename in data.get('parents', []):
                parent_data = load_json_from_search_path(parent_filename,
                        search_paths)
                # Merge data *into* parents, so we keep any overrides
                data = merge(parent_data, data)
                data['parents'].remove(parent_filename)

        message_set = cls(data.get('name', 'generic'))

        message_set.initializers = data.get('initializers', [])
        message_set.loopers = data.get('loopers', [])
        message_set.buses = cls._parse_buses(data)
        message_set.bit_numbering_inverted = data.get(
                'bit_numbering_inverted', True)
        message_set.extra_sources = set(data.get('extra_sources', set()))

        mapping_config = message_set._parse_mappings(data, search_paths,
                skip_disabled_mappings)
        message_set.initializers.extend(mapping_config['initializers'])
        message_set.loopers.extend(mapping_config['loopers'])
        message_set.extra_sources.update(mapping_config['extra_sources'])
        for message_id, message in data.get('messages', {}).items():
            message['id'] = message_id
            mapping_config['messages'].append(message)

        mapping_config['commands'].extend(data.get('commands', []))
        message_set.commands = cls._parse_commands(mapping_config['commands'])
        message_set._parse_messages(mapping_config['messages'])

        return message_set

    @classmethod
    def _parse_commands(cls, commands):
        """Parse Command Routine"""
        return [Command(**command_data) for command_data in commands]

    @classmethod
    def _parse_buses(cls, data):
        """Parse Buses Routine"""
        buses = {}
        for bus_name, bus_data in data.get('buses', {}).items():
            buses[bus_name] = CanBus(name=bus_name, **bus_data)
            if buses[bus_name].speed is None:
                fatal_error("Bus %s is missing the 'speed' attribute" %
                        bus_name)
        return buses

    def _parse_mappings(self, data, search_paths, skip_disabled_mappings):
        """Parse Mappings Routine"""
        all_messages = []
        all_commands = []
        all_extra_sources = set()
        all_initializers = []
        all_loopers = []

        for mapping in data.get('mappings', []):
            if 'mapping' not in mapping:
                fatal_error("Mapping is missing the mapping file path")

            mapping_enabled = mapping.get('enabled', True)
            if not mapping_enabled:
                LOG.warning("Mapping '%s' is disabled" % mapping['mapping'])
                if skip_disabled_mappings:
                    continue

            bus_name = mapping.get('bus', None)
            if bus_name is None:
                LOG.warning("No default bus associated with '%s' mapping" %
                        mapping['mapping'])
            elif bus_name not in self.buses:
                fatal_error("Bus '%s' (from mapping %s) is not defined" %
                        (bus_name, mapping['mapping']))

            mapping_data = load_json_from_search_path(mapping['mapping'],
                    search_paths)

            commands = mapping_data.get('commands', [])
            if not mapping_enabled:
                for command in commands:
                    command['enabled'] = False
            all_commands.extend(commands)

            if mapping_enabled:
                all_initializers.extend(mapping_data.get('initializers', []))
                all_loopers.extend(mapping_data.get('loopers', []))
                all_extra_sources.update(
                        set(mapping_data.get('extra_sources', set())))

            messages = mapping_data.get('messages', [])
            if len(messages) == 0:
                LOG.warning("Mapping file '%s' doesn't define any messages"
                        % mapping['mapping'])

            if 'database' in mapping:
                messages = merge(merge_database_into_mapping(
                                find_file(mapping['database'], search_paths),
                                messages)['messages'],
                            messages)

            for message_id, message in messages.items():
                message['id'] = message_id
                message.setdefault('bus', bus_name)
                message.setdefault('enabled', mapping_enabled)
            all_messages.extend(messages.values())

        return {'messages': all_messages,
                'commands': all_commands,
                'initializers': all_initializers,
                'extra_sources': all_extra_sources,
                'loopers': all_loopers}

    def _parse_messages(self, messages, default_bus=None):
        """Parse Messages Routine"""
        for message_data in messages:
            message_data.setdefault('bit_numbering_inverted',
                    self.bit_numbering_inverted)
            message = self.buses[message_data['bus']].get_or_create_message(
                    message_data['id'])
            message.message_set = self
            message.merge_message(message_data)
