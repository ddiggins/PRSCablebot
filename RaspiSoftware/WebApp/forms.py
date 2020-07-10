""" Creates a form to send serial commands """

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SerialSendForm(FlaskForm):
    """Serial Send"""
    json = StringField('Data', [
        DataRequired()])
    submit = SubmitField('Submit')
