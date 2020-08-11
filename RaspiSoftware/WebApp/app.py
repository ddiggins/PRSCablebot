""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """
from gevent import monkey
monkey.patch_all(thread=False)
import os
from multiprocessing import Queue, Process, Pipe
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from flask_socketio import SocketIO, emit, send
from forms import SerialSendForm
import SerialCommunication
import json
import logging
import sqlConnector
import camera as Camera
import urllib.request
from werkzeug.utils import secure_filename
from modbus import Modbus
import deployment

# Initializes flask app
APP = Flask(__name__)

# Suppresses terminal outputs of GET and POST. Only allows error messages.
LOG = logging.getLogger('werkzeug')
LOG.setLevel(logging.DEBUG)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
APP.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
SOCKETIO = SocketIO(APP, message_queue='redis://')

# Lists to display incoming and outgoing commands
INCOMING = []
OUTGOING = []

@SOCKETIO.on('send serial command')
def send_serial_command(data):
    """ Enables motor by sending json value """
    print(data)
    serial_command = data
    SERIAL_PARENT.send(serial_command)
    OUTGOING.append(serial_command)

@SOCKETIO.on('enable motor')
def enable_motor():
    """ Enables motor by sending json value """
    print('Enabling motor')
    start_motor = '{"id" : "Motor1", "enabled" : "1"}'
    SERIAL_PARENT.send(start_motor)
    OUTGOING.append(start_motor)

@SOCKETIO.on('disable motor')
def disable_motor():
    """Disables motor"""
    print('Disabling motor')
    stop_motor = '{"id" : "Motor1", "enabled" : "0"}'
    SERIAL_PARENT.send(stop_motor)
    OUTGOING.append(stop_motor)

@SOCKETIO.on('new motor power')
def update_motor_speed(data):
    """Changes the motor speed to value dictated by the slider."""
    print('sending new motor power')
    slider_power = json.dumps({"id" : "Motor1", "speed": data})
    SERIAL_PARENT.send(slider_power)
    OUTGOING.append(slider_power)

@SOCKETIO.on('new motor target')
def update_motor_target(data):
    """Changes the motor target to value dictated by the 
    encoder speed slider or position input field."""
    print('sending new motor target')
    slider_target = json.dumps({"id" : "Motor1", "target": data})
    SERIAL_PARENT.send(slider_target)
    OUTGOING.append(slider_target)

@SOCKETIO.on('new motor mode')
def update_motor_mode(data):
    print('sending new motor mode')
    """Changes the motor speed to value dictated by the slider."""
    mode = json.dumps({"id" : "Motor1", "mode": data})
    SERIAL_PARENT.send(mode)
    OUTGOING.append(mode)

# @SOCKETIO.on('run deployment')
def run_deployment(file):
    """ Runs a deployment for a given file """
    print("running deployment")
    DEPLOYER = Process(target=deployment.start_deployment,\
        args=(SERIAL_PARENT, ENCODER_CHILD, TROLL,  file))
    DEPLOYER.start()
    DEPLOYER.join()

# File filter for deployment file
ALLOWED_EXTENSIONS = set(['txt'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@APP.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    print("web page loading")

    # Upload deployment file and run deployment routine
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # 
        if file.filename == '':
            print('No file selected for uploading')
            return redirect(request.url)
        # If proper file uploaded, save file to RasPi, emit event that triggers the run deployment process 
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))
            # SOCKETIO.emit('run deployment', filename, broadcast=False)
            file_location = 'uploads/' + str(filename)
            run_deployment(file_location)
            print('File successfully uploaded')
            # Returns empty url to prevent page reload upon submission
            return '', 204

    template_data = {
        'incoming':INCOMING,
        'outgoing':OUTGOING
    }

    return render_template('robotWebapp.jinja2', **template_data)

if __name__ == '__main__':

    # Pipes to Webapp
    SERIAL_CHILD, SERIAL_PARENT = Pipe()

    # Pipes for encoder
    ENCODER_CHILD, ENCODER_PARENT = Pipe()
    
    # Queues for sql database connector
    RECORD_QUEUE = Queue()
    DATA_QUEUE = Queue()
    
    # Start AquaTROLL
    TROLL = Modbus(DATA_QUEUE)

    # Starts camera
    CAMERA_PROCESS = Process(target=Camera.start_camera, args=((2592, 1944), 300, "Images", RECORD_QUEUE))
    CAMERA_PROCESS.start()

    # Starts sql database connector that handles writing and reading(broadcasts to socket)
    DATABASE_CONNECTOR = Process(target=sqlConnector.start_sqlConnector,\
    args=(RECORD_QUEUE,DATA_QUEUE))

    # DATABASE_CONNECTOR = Process(target=sqlConnector.start_sqlConnector,\
    #     args=(RECORD_QUEUE,DATA_QUEUE, ENCODER_PARENT))
    DATABASE_CONNECTOR.start()

    # Starts thread that runs serial communication.
    COMMUNICATOR = Process(target=SerialCommunication.start_serial_communication,\
            args=(RECORD_QUEUE, SERIAL_CHILD, ENCODER_PARENT))
    COMMUNICATOR.start()

    # Runs app wrapped in Socket.io. "debug" and "use_reloader" need to be false
    # or else Flask creates a child process and re-runs main.
    SOCKETIO.run(APP, debug=False, host='0.0.0.0', use_reloader=False) 