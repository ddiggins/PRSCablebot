""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """

from gevent import monkey
monkey.patch_all()
import os
import sys
import time
import signal
from multiprocessing import Queue, Process
import threading 
from threading import Thread, Lock
from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, join_room, emit, send
from forms import SerialSendForm
import SerialCommunication
import json
import ssl 
import logging
import logger
import sqlConnector

# Initializes flask app
app = Flask(__name__)

# Suppresses terminal outputs of GET and POST. Only allows error messages.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
socketio = SocketIO(app)

# Lists to display incoming and outgoing commands
incoming = []
outgoing = []

# A mutex to protect the incoming queue
lock = Lock()

@socketio.on('enable motor')
def enable_motor():
    """ Enables motor by sending json value """
    start_motor = '{"id" : "Motor1", "enabled" : "1"}'
    outgoing_commands.put(start_motor)
    outgoing.append(start_motor)

@socketio.on('disable motor')
def disable_motor():
    """Disables motor"""
    stop_motor = '{"id" : "Motor1", "enabled" : "0"}'
    outgoing_commands.put(stop_motor)
    outgoing.append(stop_motor)

@socketio.on('new motor speed')
def update_motor_speed(data):
    """Changes the motor speed to value dictated by the slider."""
    slider_speed = json.dumps({"id" : "Motor1", "speed": data})
    outgoing_commands.put(slider_speed)
    outgoing.append(slider_speed)


@app.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    form = SerialSendForm()
    print("web page loading")

    # Submit motor command through form
    if form.validate_on_submit():
        # Send value to outgoing queue
        json = form.json.data
        outgoing_commands.put(json)
        outgoing.append(json)

    templateData = {
        'incoming':incoming,
        'outgoing':outgoing
    }

    return render_template('serialMonitor.jinja2', **templateData, form=form)


def unit_testing():
    # Queues for serial commands    
    outgoing_commands = Queue()
    incoming_commands = Queue()

    # Queues for sql database connector
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "sensorData", True, lock_global)
    request_queue_global = Queue()
    record_queue_global = Queue()
    answer_queue_global = Queue()
    connector_queues = [request_queue_global, record_queue_global, answer_queue_global, lock_global]

    connector = Process(target=connector.run_database_connector,\
        args=(request_queue_global, record_queue_global, answer_queue_global))
    connector.start()

    # Starts thread that runs serial communication.
    communicator = Process(target=SerialCommunication.run_communication,\
            args=(outgoing_commands, incoming_commands, lock))
    communicator.start()

    # Starts background task that continually checks for incoming messages.
    test_logger = logger.Logger(incoming_commands, outgoing_commands, lock, socketio, "testLog.txt", connector_queues)
    # socketio.start_background_task(new_logger.run_logger)

    # Runs app wrapped in Socket.io. "debug" and "use_reloader" need to be false 
    # or else Flask creates a child process and re-runs main. 
    socketio.run(app, debug=False, host='0.0.0.0', use_reloader=False)

    return (test_logger)

if __name__ == '__main__':
    # Queues for serial commands    
    outgoing_commands = Queue()
    incoming_commands = Queue()

    # Queues for sql database connector
    lock_global = Lock()
    connector = sqlConnector.SQLConnector("sensorLogs", "sensorData", True, lock_global)
    request_queue_global = Queue()
    record_queue_global = Queue()
    answer_queue_global = Queue()
    connector_queues = [request_queue_global, record_queue_global, answer_queue_global, lock_global]

    connector = Process(target=connector.run_database_connector,\
        args=(request_queue_global, record_queue_global, answer_queue_global))
    connector.start()

    # Starts thread that runs serial communication.
    communicator = Process(target=SerialCommunication.run_communication,\
            args=(outgoing_commands, incoming_commands, lock))
    communicator.start()

    # Starts background task that continually checks for incoming messages.
    new_logger = logger.Logger(incoming_commands, outgoing_commands, lock, socketio, "mainLog.txt", connector_queues)
    socketio.start_background_task(new_logger.run_logger)

    # Runs app wrapped in Socket.io. "debug" and "use_reloader" need to be false 
    # or else Flask creates a child process and re-runs main. 
    socketio.run(app, debug=False, host='0.0.0.0', use_reloader=False)    
