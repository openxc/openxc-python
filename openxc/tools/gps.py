"""
This module contains the methods for the ``openxc-gps`` command line program.

`main` is executed when ``openxc-gps`` is run, and all other callables in this
module are internal only.
"""
from __future__ import absolute_import

import argparse
from xml.etree import ElementTree as ET

from openxc.sources.trace import TraceDataSource
from .common import device_options, configure_logging, select_device


class GPXTranscoder(object):
    """GPX Transcoder Class"""
    ## @var root
    # The root object instance.
    ## @var track
    # The track object instance.
    ## @var number
    # The number object instance.
    ## @var segment
    # The segment object instance.
    # @var latitude
    # The latitude object instance.
    # @var longitude
    # The longitude object instance.
    
    def __init__(self):
        """Initialization Routine"""
        self.root = ET.Element("gpx")
        track = ET.SubElement(self.root, "trk")
        
        number = ET.SubElement(track, "number")
        number.text = "1"
        
        self.segment = ET.SubElement(track, "trkseg")
        
        self.latitude = self.longitude = None

    def output(self):
        """Output Routine
        @return The Element version of this object instance."""
        return ET.tostring(ET.ElementTree(self.root).getroot())

    def receive(self, message, **kwargs):
        """Receive Routine
        @param message The message to process.
        @param kwargs Additional input."""
        if message['name'] == 'latitude':
            self.latitude = message['value']
        elif message['name'] == 'longitude':
            self.longitude = message['value']

        if self.latitude and self.longitude:
            point = ET.SubElement(self.segment, "trkpt")
            point.set('lat', str(self.latitude))
            point.set('lon', str(self.longitude))
            self.latitude = self.longitude = None


def parse_options():
    """Parse Options Routine
    @return arguments The parser arguments."""
    ## #var parse
    # The parser object instance.
    parser = argparse.ArgumentParser(description=
            "Create a GPS trace in various formats from OpenXC input data")
    parser.add_argument("trace_file", metavar ='TRACEFILE',
            help="trace file to pull GPX log from")
    parser.add_argument("-f", "--format", type=str, choices=['gpx'],
            default='gpx', help="select the output format of the GPS trace")
    ## @var arguments
    # The arguments object instance.
    arguments = parser.parse_args()
    return arguments


def main():
    """Main Routine"""
    configure_logging()
    ## @var arguments
    # The arguments object instance.
    arguments = parse_options()
    ## @var transcoder
    # The transcoder object instance.
    transcoder = GPXTranscoder()
    ## @var source
    # The source object instance.
    source = TraceDataSource(transcoder.receive, filename=arguments.trace_file,
            loop=False, realtime=False)
    source.start()
    source.join()

    print(transcoder.output().decode("utf-8"))
