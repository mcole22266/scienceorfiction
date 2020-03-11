# forms.py
# Created by: Michael Cole
# Updated by: [Michael Cole]
# --------------------------
# Contains Flask Forms to be used in front-end bootstrap forms.
# Also contains custom wtform validators.

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import EqualTo, InputRequired, ValidationError


def adminAlreadyExists(form, field):
    '''
    Custom validator to raise a ValidationError if the user inputs an admin
    username that is already in-use.

    Args:
        form (FlaskForm): required by WTForms for custom validators.
        field (FlaskFormField): required by WTForms for custom validators.
    Returns:
        None
    '''
    from .extensions import getAdmin
    admin = getAdmin(username=field.data)
    if admin:
        raise ValidationError('This admin username already exists.')


def epNumAlreadyExists(form, field):
    '''
    Custom validator to raise a ValidationError if the user inputs an episode
    number that already exists in the db.

    Args:
        form (FlaskForm): required by WTForms for custom validators.
        field (FlaskFormField): required by WTForms for custom validators.
    Returns:
        None
    '''
    from .extensions import getEpisode
    episode = getEpisode(ep_num=field.data)
    if episode:
        raise ValidationError('The Episode Number you input already exists')


def participantAlreadyExists(form, field):
    '''
    Custom validator to raise a ValidationError if the user inputs a
    particpant name that already exists in the db.

    Args:
        form (FlaskForm): required by WTForms for custom validators.
        field (FlaskFormField): required by WTForms for custom validators.
    Returns:
        None
    '''
    from .extensions import getParticipant
    participant = getParticipant(name=field.data)
    if participant:
        raise ValidationError('The Participant you input already exists')


def usernameDoesNotExist(form, field):
    '''
    Custom validator to raise a ValidationError if the user inputs a username
    that does not exist in the db.

    Args:
        form (FlaskForm): required by WTForms for custom validators.
        field (FlaskFormField): required by WTForms for custom validators.
    Returns:
        None
    '''
    from .extensions import getAdmin
    admin = getAdmin(username=field.data)
    if not admin:
        raise ValidationError('This username does not exist')


def incorrectPassword(form, field):
    '''
    Custom validator to raise a ValidationError if the user inputs an
    incorrect password for the given username.

    Args:
        form (FlaskForm): required by WTForms for custom validators.
        field (FlaskFormField): required by WTForms for custom validators.
    Returns:
        None
    '''
    from .extensions import encrypt, getAdmin
    admin = getAdmin(username=form.username.data)
    if admin:
        if admin.password != encrypt(field.data):
            raise ValidationError('Password is incorrect')


class AddEntryForm(FlaskForm):
    '''
    FlaskForm object used to add a new entry to the database.
    Several fields in this form are located within the template rather
    than the FlaskForm itself.

    Args:
        FlaskForm (FlaskForm): Mandatory flask form for WTForms
    '''
    ep_num = StringField('Episode Number', validators=[
        InputRequired(),
        epNumAlreadyExists
    ])

    num_items = StringField('Number of Items', validators=[
        InputRequired()
    ])

    submitEntry = SubmitField('Add Entry')


class AddParticipantForm(FlaskForm):
    '''
    FlaskForm object used to add a new participant to the database.
    Several fields in this form are located within the template rather
    than the FlaskForm itself.

    Args:
        FlaskForm (FlaskForm): Mandatory flask form for WTForms
    '''
    name = StringField('Name', validators=[
        participantAlreadyExists
    ])

    is_rogue = BooleanField('Rogue')

    submitParticipant = SubmitField('Add Participant')


class AdminLoginForm(FlaskForm):
    '''
    FlaskForm object used to log an admin into the application.

    Args:
        FlaskForm (FlaskForm): Mandatory flask form for WTForms
    '''
    username = StringField('Username', validators=[
        usernameDoesNotExist
    ])

    password = PasswordField('Password', validators=[
        incorrectPassword
    ])

    submit = SubmitField('Log In')


class AdminCreateForm(FlaskForm):
    '''
    FlaskForm object used to create an admin.

    Args:
        FlaskForm (FlaskForm): Mandatory flask form for WTForms
    '''
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
    '''
    FlaskForm object used to authenticate an admin to ensure top approval.

    Args:
        FlaskForm (FlaskForm): Mandatory flask form for WTForms
    '''
    secretcode_input = StringField('Secret Code', validators=[
        InputRequired()
    ])

    submit = SubmitField('Create Account')
