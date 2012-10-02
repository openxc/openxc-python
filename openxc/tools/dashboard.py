#!/usr/bin/env python

import argparse
import curses
import curses.wrapper
from datetime import datetime

from openxc.sources.usb import UsbDataSource
from openxc.sources.serial import SerialDataSource
from .args import device_options

try:
    unicode
except NameError:
    # Python 3
    basestring = unicode = str

# timedelta.total_seconds() is only in 2.7, so we backport it here for 2.6
def total_seconds(delta):
    return (delta.microseconds + (delta.seconds
        + delta.days * 24 * 3600) * 10**6) / 10**6

# Thanks, SO: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num):
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, unit)
        num /= 1024.0

class DataPoint(object):
    def __init__(self, name, value_type, min_value=0, max_value=0, vocab=None,
            events=False, messages_received=0):
        self.name = name
        self.type = value_type
        self.min_value = min_value
        self.max_value = max_value
        self.range = max_value - min_value
        if self.range <= 0:
            self.range = 1
        self.event = ''
        self.bad_data = False
        self.bad_data_tally = 0
        self.current_data = None
        self.events_active = events
        self.events = []
        self.messages_received = messages_received

        # Vocab is a list of acceptable strings for CurrentValue
        self.vocab = vocab or []

        if self.events_active is True:
            for _ in range(len(self.vocab)):
                self.events.append("")

    def update(self, message):
        if self.bad_data:
            self.bad_data_tally += 1
            self.bad_data = False

        self.messages_received += 1
        self.current_data = message.get('value', None)
        if not isinstance(self.current_data, bool) and isinstance(
                self.current_data, int):
            self.current_data = float(self.current_data)
        if not isinstance(self.current_data, self.type):
            self.bad_data = True
        else:
            if isinstance(self.current_data, bool):
                return
            elif isinstance(self.current_data, unicode):
                if self.current_data in self.vocab:
                    #Save the event in the proper spot.
                    if (len(message) > 2) and (self.events_active is True):
                        self.events[self.vocab.index(self.current_data)
                                ] = message.get('event', None)
                else:
                    self.bad_data = True
            else:
                if self.current_data < self.min_value:
                    self.bad_data = True
                elif self.current_data > self.max_value:
                    self.bad_data = True

    def print_to_window(self, window, row, started_time):
        width = window.getmaxyx()[1]
        window.addstr(row, 0, self.name)
        if self.current_data is not None:
            if self.type == float and not self.bad_data:
                percent = self.current_data - self.min_value
                percent /= self.range
                count = 0
                graph = "*"
                percent -= .1
                while percent > 0:
                    graph += "-"
                    count += 1
                    percent -= .1
                graph += "|"
                count += 1
                while count < 10:
                    graph += "-"
                    count += 1
                graph += "* "
                window.addstr(row, 30, graph)

            if self.events_active is False:
                value = str(self.current_data)
            else:
                result = ""
                for item, value in enumerate(self.vocab):
                    if value == "driver":
                        keyword = "dr"
                    elif value == "passenger":
                        keyword = "ps"
                    elif value == "rear_right":
                        keyword = "rr"
                    elif value == "rear_left":
                        keyword = "rl"
                    result += "%s: %s " % (keyword, str(self.events[item]))
                value = result

            if self.bad_data:
                value += " (invalid)"
                value_color = curses.color_pair(1)
            else:
                value_color = curses.color_pair(0)
            window.addstr(row, 45, value, value_color)

        if self.bad_data_tally > 0:
            bad_data_color = curses.color_pair(1)
        else:
            bad_data_color = curses.color_pair(2)

        if width > 90:
            window.addstr(row, 80, "Errors: " + str(self.bad_data_tally),
                    bad_data_color)

        if self.messages_received > 0:
            message_count_color = curses.color_pair(0)
        else:
            message_count_color = curses.color_pair(3)

        if width > 100:
            window.addstr(row, 95, "Messages: " + str(self.messages_received),
                    message_count_color)

        if width >= 125:
            window.addstr(row, 110, "Frequency (Hz): %d" %
                    (self.messages_received /
                        (total_seconds(datetime.now() - started_time) + 0.1)))


class Dashboard(object):
    def __init__(self, window, elements):
        self.window = window
        self.elements = elements
        self.started_time = datetime.now()
        self.messages_received = 0

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)

    def receive(self, message):
        self.messages_received += 1
        if self.source.bytes_received == 0:
            self.started_time = datetime.now()
        self._redraw(message)

    def _redraw(self, message):
        for element in self.elements:
            if element.name == message.get('name', None):
                element.update(message)
                break

        self.window.erase()
        max_rows = self.window.getmaxyx()[0] - 4
        for row, element in enumerate(self.elements):
            if row > max_rows:
                break
            element.print_to_window(self.window, row, self.started_time)
        self.window.addstr(max_rows, 0,
                "Message count: %d" % self.messages_received,
                curses.A_REVERSE)
        self.window.addstr(max_rows + 1, 0,
                "Total received: %s" %
                sizeof_fmt(self.source.bytes_received),
                curses.A_REVERSE)
        self.window.addstr(max_rows + 2, 0, "Data Rate: %s" %
            sizeof_fmt(self.source.bytes_received /
                (total_seconds(datetime.now() - self.started_time)
                    + 0.1)),
             curses.A_REVERSE)
        self.window.refresh()

def parse_options():
    parser = argparse.ArgumentParser(description="Receive and print OpenXC "
        "messages over USB", parents=[device_options()])
    arguments = parser.parse_args()
    return arguments


# TODO generate this list automatically from the measurement classes...when
# those exist.
def initialize_elements():
    elements = []

    elements.append(DataPoint('steering_wheel_angle', float, -600, 600))
    elements.append(DataPoint('engine_speed', float, 0, 8000))
    elements.append(DataPoint('transmission_gear_position', unicode,
        vocab=['first', 'second', 'third', 'fourth', 'fifth', 'sixth',
            'seventh', 'eighth', 'neutral', 'reverse', 'park']))
    elements.append(DataPoint('ignition_status', unicode,
        vocab=['off', 'accessory', 'run', 'start']))
    elements.append(DataPoint('brake_pedal_status', bool))
    elements.append(DataPoint('parking_brake_status', bool))
    elements.append(DataPoint('headlamp_status', bool))
    elements.append(DataPoint('accelerator_pedal_position', float, 0, 100))
    elements.append(DataPoint('torque_at_transmission', float, -800, 1500))
    elements.append(DataPoint('vehicle_speed', float, 0, 120))
    elements.append(DataPoint('lateral_acceleration', float, -100, 100))
    elements.append(DataPoint('longitudinal_acceleration', float, -100, 100))
    elements.append(DataPoint('fuel_consumed_since_restart', float, 0, 300))
    elements.append(DataPoint('fine_odometer_since_restart', float, 0, 300))
    elements.append(DataPoint('door_status', unicode,
        vocab=['driver', 'rear_left', 'rear_right', 'passenger'], events=True))
    elements.append(DataPoint('windshield_wiper_status', bool))
    elements.append(DataPoint('odometer', float, 0, 100000))
    elements.append(DataPoint('high_beam_status', bool))
    elements.append(DataPoint('fuel_level', float, 0, 300))
    elements.append(DataPoint('latitude', float, -90, 90))
    elements.append(DataPoint('longitude', float, -180, 180))
    elements.append(DataPoint('heater_status', bool))
    elements.append(DataPoint('air_conditioning_status', bool))
    elements.append(DataPoint('charging_status', bool))
    elements.append(DataPoint('range', float, 0, 500))
    elements.append(DataPoint('gear_lever_position', unicode,
        vocab=['first', 'second', 'third', 'fourth', 'fifth', 'sixth',
            'seventh', 'neutral', 'reverse', 'park', 'drive', 'low', 'sport']))
    elements.append(DataPoint('battery_level', float, 0, 100))
    elements.append(DataPoint('cabin_temperature', float, -50, 150))

    return elements


def run_dashboard(window, source_class, source_kwargs):
    dashboard = Dashboard(window, initialize_elements())
    source = source_class(dashboard.receive, **source_kwargs)
    dashboard.source = source
    source.start()


def main():
    arguments = parse_options()

    if arguments.use_serial:
        source_class = SerialDataSource
        source_kwargs = dict(port=arguments.serial_port,
                baudrate=arguments.baudrate)
    else:
        source_class = UsbDataSource
        source_kwargs = dict(vendor_id=arguments.usb_vendor)


    curses.wrapper(run_dashboard, source_class, source_kwargs)
