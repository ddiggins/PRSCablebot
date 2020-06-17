""" Basic web app using Flask
    Runs on the local ip of the pi and is accessible on the network """
import os
from multiprocessing import Queue
import threading
from flask import Flask, render_template, url_for, redirect
from forms import SerialSendForm
import SerialCommunication

app = Flask(__name__)

# Queues for serial commands
outgoing_commands = Queue()
incoming_commands = Queue()

# Secret key to use for cookies (Definitely not secure but secure enough)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Lists to display incoming and outgoing commands
incoming = []
outgoing = []

@app.route('/', methods=('GET', 'POST'))
def index():
    """ Creates webpage. Runs every time the page is refreshed """
    form = SerialSendForm()

    while not incoming_commands.empty():  # Read all commands in the incoming queue
        line = incoming_commands.get_nowait()
        incoming.append(line)

    if form.validate_on_submit():
        # Send value to queue
        json = form.json.data
        outgoing_commands.put(json)
        outgoing.append(json)

    templateData = {
        'incoming':incoming,
        'outgoing':outgoing
    }

    return render_template('index.jinja2', **templateData, form=form)

if __name__ == '__main__':
    communicator = threading.Thread(target=SerialCommunication.run_communication,\
         args=(outgoing_commands, incoming_commands))
    communicator.start()
    app.run(debug=True, host='0.0.0.0')
