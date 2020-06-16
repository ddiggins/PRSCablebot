# basic web app using Flask
import os
from flask import Flask, render_template, url_for, redirect
from forms import SerialSendForm
from multiprocessing import Queue
import threading
import SerialCommunication

app = Flask(__name__)

outgoing_commands = Queue()
incoming_commands = Queue()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
lines = []
outgoing = []

@app.route('/', methods=('GET', 'POST'))
def index():
    form = SerialSendForm()

    while not incoming_commands.empty():
            line = incoming_commands.get_nowait()
            lines.append(line)

    if form.validate_on_submit():
        # Send value to queue
        json = form.json.data
        outgoing_commands.put(json)
        outgoing.append(json)
        
    templateData = {
        'incoming':lines,
        'outgoing':outgoing
    }

    return render_template('index.jinja2', **templateData, form=form)

if __name__ == '__main__':
    communicator = threading.Thread(target=SerialCommunication.run_communication, args=(outgoing_commands, incoming_commands))
    communicator.start()
    app.run(debug=True, host='0.0.0.0')
