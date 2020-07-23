""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """
from gevent import monkey
monkey.patch_all()
import os
from multiprocessing import Queue, Process
from threading import Lock
from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, emit, send
from forms import SerialSendForm
import SerialCommunication
import json
import logging
import logger
import sqlConnector
import camera

# Initializes flask app

APP = Flask(__name__)

# Suppresses terminal outputs of GET and POST. Only allows error messages.
LOG = logging.getLogger('werkzeug')
LOG.setLevel(logging.ERROR)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
APP.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
SOCKETIO = SocketIO(APP)

# Lists to display incoming and outgoing commands
INCOMING = []
OUTGOING = []

# A mutex to protect the incoming queue
LOCK = Lock()

@SOCKETIO.on('enable motor')
def enable_motor():
    """ Enables motor by sending json value """
    start_motor = '{"id" : "Motor1", "enabled" : "1"}'
    OUTGOING_COMMANDS.put(start_motor)
    OUTGOING.append(start_motor)

@SOCKETIO.on('disable motor')
def disable_motor():
    """Disables motor"""
    stop_motor = '{"id" : "Motor1", "enabled" : "0"}'
    OUTGOING_COMMANDS.put(stop_motor)
    OUTGOING.append(stop_motor)

@SOCKETIO.on('new motor speed')
def update_motor_speed(data):
    """Changes the motor speed to value dictated by the slider."""
    slider_speed = json.dumps({"id" : "Motor1", "speed": data})
    OUTGOING_COMMANDS.put(slider_speed)
    OUTGOING.append(slider_speed)


@APP.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    form = SerialSendForm()
    print("web page loading")

    # Submit motor command through form
    if form.validate_on_submit():
        # Send value to outgoing queue
        json_message = form.json.data
        OUTGOING_COMMANDS.put(json_message)
        OUTGOING.append(json_message)

    template_data = {
        'incoming':INCOMING,
        'outgoing':OUTGOING
    }

    return render_template('serialMonitor.jinja2', **template_data, form=form)


if __name__ == '__main__':

    # Queues for serial commands
    OUTGOING_COMMANDS = Queue()
    INCOMING_COMMANDS = Queue()

    # Queues for sql database connector
    LOCK_GLOBAL = Lock()
    CONNECTOR = sqlConnector.SQLConnector("sensorLogs", "default", False, LOCK_GLOBAL, SOCKETIO)
    REQUEST_QUEUE_GLOBAL = Queue()
    RECORD_QUEUE_GLOBAL = Queue()
    ANSWER_QUEUE_GLOBAL = Queue()
    CONNECTOR_QUEUES = [REQUEST_QUEUE_GLOBAL, RECORD_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL, LOCK_GLOBAL]

    DATABASE_CONNECTOR = Process(target=CONNECTOR.run_database_connector,\
        args=(REQUEST_QUEUE_GLOBAL, RECORD_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL))
    DATABASE_CONNECTOR.start()

    # Starts thread that checks database for incoming messages
    # DATABASE_SCANNER = Process(target=CONNECTOR.get_latest_record, \
    #     args=(REQUEST_QUEUE_GLOBAL, ANSWER_QUEUE_GLOBAL, LOCK_GLOBAL))
    # DATABASE_SCANNER.start()

    # Starts thread that runs serial communication.
    COMMUNICATOR = Process(target=SerialCommunication.run_communication,\
            args=(OUTGOING_COMMANDS, INCOMING_COMMANDS, LOCK))
    COMMUNICATOR.start()

    # Starts background task that continually checks for incoming messages.
    NEW_LOGGER = logger.Logger(INCOMING_COMMANDS, OUTGOING_COMMANDS, LOCK, SOCKETIO,\
            "mainLog.txt", CONNECTOR_QUEUES)
    SOCKETIO.start_background_task(NEW_LOGGER.run_logger)

    # Starts camera
    CAMERA_PROCESS = Process(target=camera.start_camera, args=((2592, 1944), 10, "Images", RECORD_QUEUE_GLOBAL))
    CAMERA_PROCESS.start()


    # Runs app wrapped in Socket.io. "debug" and "use_reloader" need to be false
    # or else Flask creates a child process and re-runs main.
    SOCKETIO.run(APP, debug=False, host='0.0.0.0', use_reloader=False)
