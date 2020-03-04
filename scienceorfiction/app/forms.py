from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, ValidationError


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

    is_rogue = BooleanField('Rogue')

    submit = SubmitField('Add Participant')


class AdminLoginForm(FlaskForm):

    username = StringField('Username')

    password = PasswordField('Password')

    submit = SubmitField('Log In')


class AdminCreateForm(FlaskForm):

    username = StringField('Username', validators=[
        adminAlreadyExists
    ])

    password = PasswordField('Password', validators=[
        EqualTo('passwordConfirm', message='Passwords do not match.')
    ])

    passwordConfirm = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords do not match.')
    ])

    submit = SubmitField('Create Account')


class AdminAuthenticateForm(FlaskForm):

    secret_code = StringField('Secret Code')

    submit = SubmitField('Create Account')
