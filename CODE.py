from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from openxc.interface import UsbVehicleInterface
import threading
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)
socketio = SocketIO(app,async_mode="gevent")

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

if __name__ == "__main__": 
    socketio.start_background_task(vehicle_data_thread)
    app.run()


