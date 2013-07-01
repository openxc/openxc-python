#!/usr/bin/env python

"""
@file    openxc-python\openxc\tools\generate_code.py Generate Code Tools Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   This module is the main entry point for generating vehicle interface 
         source code from JSON mappings.

         Given one or more JSON mapping filenames, and a list of directories 
         where configuration files may be found, it parses the mappings, 
         validates them, and prints the resulting source to stdout."""

from __future__ import print_function
import sys
import argparse
import logging

from openxc.generator.coder import CodeGenerator
from openxc.generator.message_sets import JsonMessageSet
from openxc.utils import fatal_error, load_json_from_search_path
from .common import configure_logging

## @var LOG
# The logging object instance.
LOG = logging.getLogger(__name__)

## @var DEFAULT_SEARCH_PATH
# The default search path
DEFAULT_SEARCH_PATH = "."


def parse_options():
    """Parse Options Routine"""
    parser = argparse.ArgumentParser(description="Generate C++ source code "
            "from CAN signal descriptions in JSON")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--message-sets",
            type=str,
            nargs='+',
            dest="message_sets",
            metavar="MESSAGE_SET",
            help="generate source from these JSON-formatted message "
                    "set definitions")
    group.add_argument("--super-set",
            type=str,
            dest="super_set",
            metavar="SUPERSET",
            help="generate source with multiple active message sets, defined in"
                    " this JSON-formatted superset")
    parser.add_argument("-s", "--search-paths",
            type=str,
            nargs='+',
            dest="search_paths",
            metavar="PATH",
            help="add directories to the search path when using relative paths")

    return parser.parse_args()


def main():
    """Main Routine
    @todo dump last print to a filename or pipe instead."""
    configure_logging()
    arguments = parse_options()

    search_paths = arguments.search_paths or []
    search_paths.insert(0, DEFAULT_SEARCH_PATH)

    message_sets = arguments.message_sets or []
    if arguments.super_set is not None:
        super_set_data = load_json_from_search_path(arguments.super_set,
                arguments.search_paths)
        super_set_message_sets = super_set_data.get('message_sets', [])
        if len(super_set_message_sets) == 0:
            LOG.warning("Superset '%s' has no message sets" %
                    super_set_data.get('name', 'unknown'))
        message_sets.extend(super_set_message_sets)

    generator = CodeGenerator(search_paths)
    for filename in message_sets:
        message_set = JsonMessageSet.parse(filename, search_paths=search_paths,
                skip_disabled_mappings=True)
        if not message_set.validate_messages() or not message_set.validate_name():
            fatal_error("unable to generate code")
        generator.message_sets.append(message_set)

    # TODO dump to a filename or pipe instead
    print(generator.build_source())


if __name__ == "__main__":
    sys.exit(main())
