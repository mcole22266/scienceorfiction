from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import ValidationError, InputRequired


def adminAlreadyExists(form, field):
    from .models import Admins
    if Admins.query.filter_by(username=field.data).first():
        raise ValidationError('This admin username already exists.')


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

    password = PasswordField('Password')

    submit = SubmitField('Login')


class AdminCreateForm(FlaskForm):

    username = StringField('Username', validators=[
        adminAlreadyExists
    ])

    password = PasswordField('Password')

    submit = SubmitField('Create Account')


class AdminAuthenticateForm(FlaskForm):

    secret_code = StringField('Secret Code')

    submit = SubmitField('Create Account')
