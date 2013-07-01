
"""
@file    openxc-python\openxc\tools\dashboard.py Dashboard Tools Script
@author  Christopher Peplin github@rhubarbtech.com
@date    June 25, 2013
@version 0.9.4

@brief   This module contains the methods for the ``openxc-dashboard`` command 
         line program.

         `main` is executed when ``openxc-dashboard`` is run, and all other 
         callables in this module are internal only."""

from __future__ import absolute_import

import argparse
import curses
import numbers
from datetime import datetime

from .common import device_options, configure_logging, select_device
from openxc.vehicle import Vehicle
from openxc.measurements import EventedMeasurement, NumericMeasurement, \
        Measurement
import openxc.measurements as measurements

try:
    unicode
except NameError:
    ## @var basestring
    # Definitions for Python 3
    basestring = unicode = str

## @var DASHBOARD_MEASUREMENTS
# Dashboard measurements definition as a list.
DASHBOARD_MEASUREMENTS  = [measurements.AcceleratorPedalPosition,
                measurements.FuelLevel,
                measurements.VehicleSpeed,
                measurements.EngineSpeed,
                measurements.FuelConsumed,
                measurements.Latitude,
                measurements.Longitude,
                measurements.Odometer,
                measurements.SteeringWheelAngle,
                measurements.TorqueAtTransmission,
                measurements.LateralAcceleration,
                measurements.LongitudinalAcceleration,
                measurements.BrakePedalStatus,
                measurements.HeadlampStatus,
                measurements.HighBeamStatus,
                measurements.ParkingBrakeStatus,
                measurements.WindshieldWiperStatus,
                measurements.IgnitionStatus,
                measurements.TransmissionGearPosition,
                measurements.TurnSignalStatus,
                measurements.ButtonEvent,
                measurements.DoorStatus]


def total_seconds(delta):
    """ timedelta.total_seconds() is only in 2.7, so we backport it here for 
    2.6
    @param delta The time delta.
    """
    return (delta.microseconds + (delta.seconds
        + delta.days * 24 * 3600) * 10**6) / 10**6

def sizeof_fmt(num):
    """ Thanks, SO: http://stackoverflow.com/q/1094841/
    @param num The number of bytes to obtain in a formatted measurement."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, unit)
        num /= 1024.0

class DataPoint(object):
    """DataPoint Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    ## @var event
    # The event object instance.
    ## @var bad_data
    # Stores the number of times bad data is submitted.
    ## @var current_data
    # Stores the current data value
    ## @var events
    # Stores a dictionary containing the events.
    ## @var messages_received
    # Stores the number of messages received.
    ## @var measurement_type
    # Stores the measurement type for this object instance.
    
    def __init__(self, measurement_type):
        """Initialization Routine
        @param measurement_type The measurement type."""
        self.event = ''    
        self.bad_data = 0
        self.current_data = None
        self.events = {}
        self.messages_received = 0
        self.measurement_type = measurement_type
    
    def update(self, measurement):
        """Update Routine
        @param measurement The measurement instance."""
        self.messages_received += 1
        self.current_data = measurement
        if isinstance(measurement, EventedMeasurement):
            if measurement.valid_state():
                self.events[measurement.value] = measurement.event
            else:
                self.bad_data += 1
        elif (isinstance(measurement, NumericMeasurement) and not
                measurement.within_range()):
            self.bad_data += 1

    def print_to_window(self, window, row, started_time):
        """Print to Window Routine
        @param window The window instance.
        @param row The row instance.
        @param started_time The started time object"""
        width = window.getmaxyx()[1]
        window.addstr(row, 0, self.measurement_type.name)
        if self.current_data is not None:
            if (self.measurement_type.DATA_TYPE == numbers.Number and
                    self.bad_data == 0):
                # TODO leaking the unit class member here
                percent = ((self.current_data.value.num -
                    self.measurement_type.valid_range.min) /
                        float(self.measurement_type.valid_range.spread)) * 100
                chunks = int((percent - .1) * .1)
                graph = "*%s|%s*" % ("-" * chunks, "-" * (10 - chunks))
                window.addstr(row, 30, graph)

            if len(self.events) == 0:
                value = str(self.current_data)
            else:
                result = ""
                for item, value in enumerate(self.measurement_type.states):
                    # TODO missing keys here?
                    result += "%s: %s " % (value, self.events.get(item, "?"))
                value = result

            if self.bad_data > 0:
                value += " (invalid)"
                value_color = curses.color_pair(1)
            else:
                value_color = curses.color_pair(0)
            window.addstr(row, 45, value, value_color)

        if self.bad_data > 0:
            bad_data_color = curses.color_pair(1)
        else:
            bad_data_color = curses.color_pair(2)

        if width > 90:
            window.addstr(row, 80, "Errors: %d" % self.bad_data,
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
    """Dashboard Class
    @author  Christopher Peplin github@rhubarbtech.com
    @date    June 25, 2013
    @version 0.9.4"""
    
    def __init__(self, window, vehicle):
        """Initialization Routine
        @param window The window instance.
        @param vehicle The vehicle instance."""
        ## @var window
        # The window object instance.
        self.window = window
        ## @var elements
        # The elements dictionary.
        self.elements = {}
        for measurement_type in DASHBOARD_MEASUREMENTS:
            self.elements[Measurement.name_from_class(
                    measurement_type)] = DataPoint(measurement_type)
            vehicle.listen(measurement_type, self.receive)
        ## @var started_time
        # The dashboard start time.
        self.started_time = datetime.now()
        ## @var messages_received
        # Stores the number of stored messages.
        self.messages_received = 0

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)

    def receive(self, measurement, data_remaining=False, **kwargs):
        """Receive Routine
        @param measurement The measurement instance.
        @param data_remaining Boolean value indicating if there is more data.
        @param kwargs Additional values."""
        if self.messages_received == 0:
            self.started_time = datetime.now()
        self.messages_received += 1

        self.elements[measurement.name].update(measurement)
        if not data_remaining:
            self._redraw()


    def _redraw(self):
        """The redraw routine"""
        self.window.erase()
        max_rows = self.window.getmaxyx()[0] - 4
        for row, element in enumerate(sorted(self.elements.values(),
                key=lambda elt: elt.measurement_type.name)):
            if row > max_rows:
                break
            element.print_to_window(self.window, row, self.started_time)
        self.window.addstr(max_rows + 1, 0,
                "Message count: %d (%d corrupted)" % (self.messages_received,
                    self.source.corrupted_messages), curses.A_REVERSE)
        self.window.addstr(max_rows + 2, 0,
                "Total received: %s" %
                sizeof_fmt(self.source.bytes_received),
                curses.A_REVERSE)
        self.window.addstr(max_rows + 3, 0, "Data Rate: %s" %
            sizeof_fmt(self.source.bytes_received /
                (total_seconds(datetime.now() - self.started_time)
                    + 0.1)),
             curses.A_REVERSE)
        self.window.refresh()


def run_dashboard(window, source_class, source_kwargs):
    """Run Dashboard Routine
    @param window The window instance.
    @param The source_class instance.
    @param source_kwargs Additional input parameters."""
    vehicle = Vehicle()
    dashboard = Dashboard(window, vehicle)
    dashboard.source = source_class(**source_kwargs)
    vehicle.add_source(dashboard.source)

    while True:
        import time
        time.sleep(5)


def parse_options():
    """Parse Options Routine"""
    parser = argparse.ArgumentParser(
            description="View a real-time dashboard of all OpenXC measurements",
            parents=[device_options()])
    arguments = parser.parse_args()
    return arguments


def main():
    """Main Routine"""
    configure_logging()
    arguments = parse_options()
    source_class, source_kwargs = select_device(arguments)
    curses.wrapper(run_dashboard, source_class, source_kwargs)
