from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired


class AddEntryForm(FlaskForm):

    ep_num = StringField('Episode Number', validators=[
        InputRequired()
    ])

    num_items = StringField('Number of Items', validators=[
        InputRequired()
    ])

    submit = SubmitField('Add Entry')


class AddParticipantForm(FlaskForm):

    name = StringField('Name')

    submit = SubmitField('Add Participant')


class AdminLoginForm(FlaskForm):

    username = StringField('Username')

    password = StringField('Password')

    submit = SubmitField('Admin Login')


class AdminCreateForm(FlaskForm):

    username = StringField('Username')

    password = StringField('Password')

    secret_code = StringField('Secret Code')

    submit = SubmitField('Create Admin Account')
