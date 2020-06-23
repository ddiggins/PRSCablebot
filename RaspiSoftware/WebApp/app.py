""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """
import os
import time
from multiprocessing import Queue
import threading 
from threading import Thread
from flask import Flask, render_template, url_for, redirect
from flask_socketio import SocketIO, join_room, emit, send
from forms import SerialSendForm
import SerialCommunication
from gevent import monkey
import json

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

monkey.patch_all()
app = Flask(__name__)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
socketio = SocketIO(app)

# Lists to display incoming and outgoing commands
incoming = []
outgoing = []

def check_incoming(incoming_commands):
    """Function that checks whether there are new incoming serial messages. 
    Will run continuously as a background task."""
    while 1:
        if not incoming_commands.empty():
            #fetches message from queue and deletes that line.
            line = incoming_commands.get_nowait()
            incoming.append(line)
            socketio.emit('new incoming', line, json = True)
        time.sleep(1) # Yield

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
        # Send value to queue
        json = form.json.data
        outgoing_commands.put(json)
        outgoing.append(json)

    templateData = {
        'incoming':incoming,
        'outgoing':outgoing
    }

    return render_template('serialMonitor.jinja2', **templateData, form=form)

if __name__ == '__main__':
    # Queues for serial commands
    outgoing_commands = Queue()
    incoming_commands = Queue()
    # Starts thread that runs serial communication.
    communicator = threading.Thread(target=SerialCommunication.run_communication,\
         args=(outgoing_commands, incoming_commands))
    communicator.start()
    # app.run(debug=True, host='0.0.0.0')
    # Starts background task that continually checks for incoming messages.
    socketio.start_background_task(check_incoming, incoming_commands)
    socketio.run(app, debug=True, host='0.0.0.0')
