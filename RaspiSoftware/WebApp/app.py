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

monkey.patch_all()

app = Flask(__name__)

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize Socket.io
# socketio = SocketIO(app, message_queue='redis://')
socketio = SocketIO(app)

# Lists to display incoming and outgoing commands
incoming = []
outgoing = []

# Function that checks whether there is new incoming serial messages.
# Will run continuously as a background task.
def check_incoming(incoming_commands):
    while 1:
        if not incoming_commands.empty():
            line = incoming_commands.get_nowait() #
            incoming.append(line)
            print("incoming message", flush=True)
            socketio.emit('new incoming', line, json = True)
            print("emitted?", flush=True)

        time.sleep(0) # Yield
# What I want: If there is a new incoming, emit that new incoming and then the 
# html can just read it and put it in a table 
        
@app.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    form = SerialSendForm()
    print("web page loading")

    # Create thread to run check_incoming to detect incoming messages
    # global thread
    # print("thread is: " + str(thread))
    # if thread is None:
    #     print("Thread starting")
    #     thread = threading.Thread(target=check_incoming, args=([incoming_commands]))
    #     thread.start()

    # while not incoming_commands.empty():  # Read all commands in the incoming queue
    #     line = incoming_commands.get_nowait()
    #     incoming.append(line)

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

@socketio.on('stop')
def on_stop():
    """Stops website from running"""

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
