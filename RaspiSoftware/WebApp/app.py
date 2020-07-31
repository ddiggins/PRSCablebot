""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """
from gevent import monkey
monkey.patch_all(thread=False)
import os
from multiprocessing import Queue, Process, Pipe
from threading import Lock
from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, emit, send
from forms import SerialSendForm
import SerialCommunication
import json
import logging
import sqlConnector
import camera as Camera
from Modbus import Modbus

# Initializes flask app

APP = Flask(__name__)

# Suppresses terminal outputs of GET and POST. Only allows error messages.
LOG = logging.getLogger('werkzeug')
LOG.setLevel(logging.ERROR)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
APP.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
SOCKETIO = SocketIO(APP, message_queue='redis://')

# Lists to display incoming and outgoing commands
INCOMING = []
OUTGOING = []

# A mutex to protect the incoming queue
LOCK = Lock()

@SOCKETIO.on('enable motor')
def enable_motor():
    """ Enables motor by sending json value """
    start_motor = '{"id" : "Motor1", "enabled" : "1"}'
    SERIAL_PARENT.send(start_motor)
    OUTGOING.append(start_motor)

@SOCKETIO.on('disable motor')
def disable_motor():
    """Disables motor"""
    stop_motor = '{"id" : "Motor1", "enabled" : "0"}'
    SERIAL_PARENT.send(stop_motor)
    OUTGOING.append(stop_motor)

@SOCKETIO.on('new motor speed')
def update_motor_speed(data):
    """Changes the motor speed to value dictated by the slider."""
    slider_speed = json.dumps({"id" : "Motor1", "speed": data})
    SERIAL_PARENT.send(slider_speed)
    OUTGOING.append(slider_speed)

@SOCKETIO.on('update table')
def validatesensing():
    print("recieved message from sqlConnector.py")

@APP.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    form = SerialSendForm()
    print("web page loading")

    # Submit motor command through form
    if form.validate_on_submit():
        # Send value to outgoing queue
        json_message = form.json.data
        SERIAL_PARENT.send(json_message)
        OUTGOING.append(json_message)

    template_data = {
        'incoming':INCOMING,
        'outgoing':OUTGOING
    }

    return render_template('serialMonitor.jinja2', **template_data, form=form)

if __name__ == '__main__':

    # # Pipes to Webapp
    SERIAL_CHILD, SERIAL_PARENT = Pipe()
    
    # # Queues for sql database connector
    RECORD_QUEUE = Queue()
    
    
    # Starts camera
    CAMERA_PROCESS = Process(target=Camera.start_camera, args=((2592, 1944), 10, "Images", RECORD_QUEUE))
    CAMERA_PROCESS.start()

    # Starts sql database connector that handles writing and reading(broadcasts to socket)
    DATABASE_CONNECTOR = Process(target=sqlConnector.start_sqlConnector,\
        args=(RECORD_QUEUE,))
    DATABASE_CONNECTOR.start()

    # Starts thread that runs serial communication.
    COMMUNICATOR = Process(target=SerialCommunication.start_serial_communication,\
            args=(RECORD_QUEUE, SERIAL_CHILD))
    COMMUNICATOR.start()


    # Runs app wrapped in Socket.io. "debug" and "use_reloader" need to be false
    # or else Flask creates a child process and re-runs main.
    SOCKETIO.run(APP, debug=False, host='0.0.0.0', use_reloader=False) 