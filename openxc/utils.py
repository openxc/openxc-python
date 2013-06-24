"""Data containers and other utilities."""
import time
import json
import collections
import logging
import os
import sys

LOG = logging.getLogger(__name__)

class Range(object):
    """Encapsulates a ranged defined by a min and max numerical value."""
    def __init__(self, minimum, maximum):
        self.min = minimum
        self.max = maximum

    def within_range(self, value):
        """Returns True if the value is between this Range, inclusive."""
        return value >= self.min and value <= self.max

    @property
    def spread(self):
        """Returns the spread between this Range's min and max."""
        return self.max - self.min


class AgingData(object):
    """Mixin to associate a class with a time of birth."""

    def __init__(self):
        self.created_at = time.time()

    @property
    def age(self):
        """Return the age of the data in seconds."""
        return time.time() - self.created_at


def quacks_like_dict(object):
    """Check if object is dict-like"""
    return isinstance(object, collections.Mapping)


def quacks_like_list(object):
    """Check if object is list-like"""
    return hasattr(object, '__iter__') and hasattr(object, 'append')


def merge(a, b):
    """Merge two deep dicts non-destructively

    Uses a stack to avoid maximum recursion depth exceptions

    >>> a = {'a': 1, 'b': {1: 1, 2: 2}, 'd': 6}
    >>> b = {'c': 3, 'b': {2: 7}, 'd': {'z': [1, 2, 3]}}
    >>> c = merge(a, b)
    >>> from pprint import pprint; pprint(c)
    {'a': 1, 'b': {1: 1, 2: 7}, 'c': 3, 'd': {'z': [1, 2, 3]}}
    """
    assert quacks_like_dict(a), quacks_like_dict(b)
    dst = a.copy()

    stack = [(dst, b)]
    while stack:
        current_dst, current_src = stack.pop()
        for key in current_src:
            if key not in current_dst:
                current_dst[key] = current_src[key]
            else:
                if (quacks_like_dict(current_src[key]) and
                        quacks_like_dict(current_dst[key])):
                    stack.append((current_dst[key], current_src[key]))
                elif (quacks_like_list(current_src[key]) and
                        quacks_like_list(current_dst[key])):
                    current_dst[key].extend(current_src[key])
                else:
                    current_dst[key] = current_src[key]
    return dst


def find_file(filename, search_paths):
    for search_path in search_paths:
        if filename[0] != '/':
            full_path = "%s/%s" % (search_path, filename)
        else:
            full_path = filename
        if os.path.exists(full_path):
            return full_path
    fatal_error("Unable to find '%s' in search paths (%s)" % (
            filename, search_paths))


def load_json_from_search_path(filename, search_paths):
    with open(find_file(filename, search_paths)) as json_file:
        try:
            data = json.load(json_file)
        except ValueError as e:
            fatal_error("%s does not contain valid JSON: \n%s\n" %
                    (filename, e))
        else:
            return data

def fatal_error(message):
    LOG.error(message)
    sys.exit(1)
