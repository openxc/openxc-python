from __future__ import absolute_import

import argparse
from xml.etree import ElementTree as ET

from openxc.sources.trace import TraceDataSource
from .common import device_options, configure_logging, select_device


class GPXTranscoder(object):
    def __init__(self):
        self.root = ET.Element("gpx")
        track = ET.SubElement(self.root, "trk")
        number = ET.SubElement(track, "number")
        number.text = "1"
        self.segment = ET.SubElement(track, "trkseg")
        self.latitude = self.longitude = None

    def add(self, latitude, longitude):
        pass

    def output(self):
        return ET.tostring(ET.ElementTree(self.root).getroot())

    def receive(self, message):
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
    parser = argparse.ArgumentParser(description=
            "Create a GPS trace in various formats from OpenXC input data",
            parents=[device_options()])
    parser.add_argument("--format", type=str, choices=['gpx'], default='gpx')
    arguments = parser.parse_args()
    return arguments


def main():
    configure_logging()
    arguments = parse_options()

    source_class, source_kwargs = select_device(arguments)
    if source_class == TraceDataSource:
        source_kwargs['loop'] = False
        source_kwargs['realtime'] = False

    transcoder = GPXTranscoder()

    source = source_class(transcoder.receive, **source_kwargs)
    source.start()

    print(transcoder.output())
