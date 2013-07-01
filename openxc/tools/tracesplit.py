
"""
@file    openxc-python\openxc\tools\tracesplit.py Trace Split Tools Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   This module contains the methods for the ``openxc-trace-split`` 
         command line program.

         `main` is executed when ``openxc-trace-split`` is run, and all other 
         callables in this module are internal only."""

from __future__ import absolute_import

import argparse
import datetime
from operator import itemgetter
from collections import defaultdict

from openxc.formats.json import JsonFormatter
from openxc.sources.trace import TraceDataSource
from .common import configure_logging


class BaseSplitter(object):
    """Base Splitter Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var records
    # The records instance.
    ## @var buckets
    # The buckets instance.
    
    def __init__(self):
        """Initialization Routine"""
        self.records = []
        self.buckets = defaultdict(list)

    def _key_for_record(self, record):
        """Key For Record Routine
        @param record The input record.
        @exception NotImplementedError Returned if not implemented."""
        raise NotImplementedError

    def split(self, files):
        """Split Routine
        @param files Object with a list of files to process."""
        for filename in files:
            source = TraceDataSource(self.receive, filename=filename,
                    loop=False, realtime=False)
            source.start()

        self.records.sort(key=itemgetter('timestamp'))
        for record in self.records:
            self.buckets[self._key_for_record(record)].append(record)

        return self.buckets

    def receive(self, message, **kwargs):
        """Receive Routine"""
        self.records.append(message)


class TimeSplitter(BaseSplitter):
    """Time Splitter Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var unit
    # The unit instance.
    
    def __init__(self, unit):
        """Initialization Routine
        @param unit The unit instance."""
        super(TimeSplitter, self).__init__()
        self.unit = unit

    def _key_for_record(self, record):
        """Key For Record Routine
        @param record The input record"""
        date = datetime.datetime.fromtimestamp(record['timestamp'])
        if self.unit == "day":
            date_format = '%Y-%m-%d'
        elif self.unit == "hour":
            date_format = '%Y-%m-%d-%H'
        return date.strftime(date_format)
        
class TripSplitter(BaseSplitter):
    """Trip Splitter Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4
    @todo allow overriding this at the command line."""
    
    ## @var MAXIMUM_RECORD_GAP_SECONDS
    # Maximum Record Gap Seconds
    MAXIMUM_RECORD_GAP_SECONDS = 600
    ## @var last_timestamp
    # The last timestamp instance.
    ## @var current_trip_key
    # The current trip key object instance.
        
    def _key_for_record(self, record):
        """Key For Record Routine
        @param record The input record"""
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
    """Parse Options Routine"""
    parser = argparse.ArgumentParser(description="Split a collection of "
            "OpenXC trace files by day, hour or trips")
    parser.add_argument("files", action="store", nargs='+', default=False)
    parser.add_argument("-s", "--split", action="store",
            choices=['day', 'hour', 'trip'], default="trip",
            help="select the time unit to split the combined trace files")
    
    arguments = parser.parse_args()
    return arguments


def main():
    """Main Routine"""
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
