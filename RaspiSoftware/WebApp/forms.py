from flask_wtf import FlaskForm,
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SerialSendForm(FlaskForm):
    """Serial Send"""
    data = StringField('Data', [
        DataRequired()])
    submit = SubmitField('Submit')