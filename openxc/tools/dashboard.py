""" This module contains the methods for the ``openxc-dashboard`` command line
program.

`main` is executed when ``openxc-dashboard`` is run, and all other callables in
this module are internal only.
"""

import argparse
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from openxc.interface import UsbVehicleInterface
import threading
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
socketio = SocketIO(app)

def vehicle_data_thread():
    vi = UsbVehicleInterface(callback=send_data)
    vi.start()

def send_data(data, **kwargs):
    socketio.emit('vehicle data', data, broadcast=True)

@app.route("/")
def dashboard_static():
    try:
        vehicle_data_thread()
    except:
        pass
    return render_template('dashboard.html')

def parse_options():
    parser = argparse.ArgumentParser(
            description="View a real-time dashboard of all OpenXC measurements",
            parents=[device_options()])
    arguments = parser.parse_args()
    return arguments


def main():
    socketio.start_background_task(vehicle_data_thread)
    print("View the dashboard at http://127.0.0.1:5000")
    app.run()
