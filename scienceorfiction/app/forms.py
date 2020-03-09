from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, ValidationError


def adminAlreadyExists(form, field):
    from .extensions import getAdmin
    admin = getAdmin(username=field.data)
    if admin:
        raise ValidationError('This admin username already exists.')


def epNumAlreadyExists(form, field):
    from .extensions import getEpisode
    episode = getEpisode(ep_num=field.data)
    if episode:
        raise ValidationError('The Episode Number you input already exists')


def participantAlreadyExists(form, field):
    from .extensions import getParticipant
    participant = getParticipant(name=field.data)
    if participant:
        raise ValidationError('The Participant you input already exists')


def usernameDoesNotExist(form, field):
    from .extensions import getAdmin
    admin = getAdmin(username=field.data)
    if not admin:
        raise ValidationError('This username does not exist')


def incorrectPassword(form, field):
    from .extensions import encrypt, getAdmin
    admin = getAdmin(username=form.username.data)
    if admin:
        if admin.password != encrypt(field.data):
            raise ValidationError('Password is incorrect')


class AddEntryForm(FlaskForm):

    ep_num = StringField('Episode Number', validators=[
        InputRequired(),
        epNumAlreadyExists
    ])

    num_items = StringField('Number of Items', validators=[
        InputRequired()
    ])

    submit = SubmitField('Add Entry')


class AddParticipantForm(FlaskForm):

    name = StringField('Name', validators=[
        participantAlreadyExists
    ])

    is_rogue = BooleanField('Rogue')

    submit = SubmitField('Add Participant')


class AdminLoginForm(FlaskForm):

    username = StringField('Username', validators=[
        usernameDoesNotExist
    ])

    password = PasswordField('Password', validators=[
        incorrectPassword
    ])

    submit = SubmitField('Log In')


class AdminCreateForm(FlaskForm):

    username = StringField('Username', validators=[
        adminAlreadyExists
    ])

    firstname = StringField('First Name', render_kw={
        'placeholder': 'optional'
    })

    lastname = StringField('Last Name', render_kw={
        'placeholder': 'optional'
    })

    password = PasswordField('Password', validators=[
        EqualTo('passwordConfirm', message='Passwords do not match.')
    ])

    passwordConfirm = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords do not match.')
    ])

    submit = SubmitField('Create Account')


class AdminAuthenticateForm(FlaskForm):

    secretcode_input = StringField('Secret Code')

    submit = SubmitField('Create Account')
