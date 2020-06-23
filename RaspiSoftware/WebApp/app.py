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

app = Flask(__name__)
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
lock = Lock()
started = 0

def check_incoming(incoming_commands, lock):
    """Function that checks whether there are new incoming serial messages. 
    Will run continuously as a background task."""
    while 1:
        lock.acquire()
        if not incoming_commands.empty():
            #fetches message from queue and deletes that line.
            # time.sleep(.1)
            line = incoming_commands.get_nowait()
            # print("json incoming", line)
            incoming.append(line)
            socketio.emit('new incoming', line, json = True)
        lock.release()
        time.sleep(.05) # Yield

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

    if started == 0:
    # Queues for serial commands
        outgoing_commands = Queue()
        incoming_commands = Queue()
        print("MAIN STARTED")
        print("Started is: " + str(started) + "At Beginning")
        # Starts thread that runs serial communication.
        communicator = Process(target=SerialCommunication.run_communication,\
             args=(outgoing_commands, incoming_commands, lock))
        communicator.start()
        # # Starts background task that continually checks for incoming messages.
        socketio.start_background_task(check_incoming, incoming_commands, lock)
        # socketio.start_background_task(SerialCommunication.run_communication, outgoing_commands, incoming_commands, lock)
        # background = Process(target=check_incoming,\
        #      args=(incoming_commands, lock))
        time.sleep(2)

        outgoing_commands.put('{"id" : "Motor1", "enabled" : "1"}')

        print("sleeping")
        time.sleep(5)
        print("Starting App")

        started = 1
        print("Started is: " + str(started))
        socketio.run(app, debug=False, host='0.0.0.0', use_reloader=False)
        # app.run(debug=False, host='0.0.0.0', use_reloader=False)


        print("MAIN IS STILL RUNNING")

