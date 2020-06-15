# basic web app using Flask
from flask import Flask, render_template, url_for, redirect
from forms import SerialSendForm

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():
    form = SerialSendForm()
    if form.validate_on_submit():
        return redirect(url_for('success'))
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
