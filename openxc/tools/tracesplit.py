"""
This module contains the methods for the ``openxc-trace-split`` command line
program.

`main` is executed when ``openxc-trace-split`` is run, and all other callables
in this module are internal only.
"""
from __future__ import absolute_import

import argparse
import datetime
from operator import itemgetter
from collections import defaultdict

from openxc.formats.json import JsonFormatter
from openxc.sources.trace import TraceDataSource
from .common import configure_logging


class BaseSplitter(object):
    def __init__(self):
        self.records = []
        self.buckets = defaultdict(list)

    def _key_for_record(self, record):
        raise NotImplementedError

    def split(self, files):
        for filename in files:
            source = TraceDataSource(self.receive, filename=filename,
                    loop=False, realtime=False)
            source.start()

        self.records.sort(key=itemgetter('timestamp'))
        for record in self.records:
            self.buckets[self._key_for_record(record)].append(record)

        return self.buckets

    def receive(self, message):
        self.records.append(message)


class TimeSplitter(BaseSplitter):
    def __init__(self, unit):
        super(TimeSplitter, self).__init__()
        self.unit = unit

    def _key_for_record(self, record):
        date = datetime.datetime.fromtimestamp(record['timestamp'])
        if self.unit == "day":
            date_format = '%Y-%m-%d'
        elif self.unit == "hour":
            date_format = '%Y-%m-%d-%H'
        return date.strftime(date_format)


class TripSplitter(BaseSplitter):
    # TODO allow overriding this at the command line
    MAXIMUM_RECORD_GAP_SECONDS = 600

    def _key_for_record(self, record):
        timestamp = record['timestamp']
        last_timestamp = getattr(self, 'last_timestamp', None)
        if last_timestamp is not None:
            if (timestamp - last_timestamp) > self.MAXIMUM_RECORD_GAP_SECONDS:
                self.current_trip_key = timestamp
        else:
            self.current_trip_key = timestamp
        self.last_timestamp = timestamp
        return datetime.datetime.fromtimestamp(self.last_timestamp).strftime(
                "%Y-%m-%d-%H.%M")


def parse_options():
    parser = argparse.ArgumentParser(description="Split a collection of "
            "OpenXC trace files by day, hour or trips")
    parser.add_argument("files", action="store", nargs='+', default=False)
    parser.add_argument("-s", "--split", action="store",
            choices=['day', 'hour', 'trip'], default="trip",
            help="select the time unit to split the combined trace files")

    arguments = parser.parse_args()
    return arguments


def main():
    configure_logging()
    arguments = parse_options()

    if arguments.split == 'trip':
        splitter = TripSplitter()
    else:
        splitter = TimeSplitter(arguments.split)

    for key, split in splitter.split(arguments.files).items():
        with open("%s.json" % key, 'w') as output_file:
            for record in split:
                output_file.write(JsonFormatter.serialize(record) + "\n")
