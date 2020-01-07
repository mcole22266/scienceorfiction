from flask_wtf import FlaskForm

from wtforms import StringField, DateField, SelectMultipleField, SubmitField
from wtforms.validators import InputRequired
from wtforms.widgets import ListWidget, CheckboxInput


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class AddEntryForm(FlaskForm):

    ep_num = StringField('Episode Number', validators=[
        InputRequired()
    ])

    date = DateField('Date', validators=[
        InputRequired()
    ])

    submit = SubmitField('Add Entry')


class AddParticipantForm(FlaskForm):

    name = StringField('Name')

    submit = SubmitField('Add Participant')
