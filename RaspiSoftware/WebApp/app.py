# basic web app using Flask
import os
from flask import Flask, render_template, url_for, redirect
from forms import SerialSendForm

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=('GET', 'POST'))
def index():
    form = SerialSendForm()
    # Get queue
    templateData = {
        'incoming':"Abetrary Value",
        'outgoing':"Abetrary Value"
    }
    if form.validate_on_submit():
        # Send value to queue
        json = form.json.data
    return render_template('index.jinja2', **templateData, form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
