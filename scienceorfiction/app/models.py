# Contains all database models for Flask-SQLAlchemy as well as
# the db object created upon initialization

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from .extensions import login_manager

db = SQLAlchemy()  # create db object


@login_manager.user_loader
def load_user(id):
    '''
    Mandatory function for login_manager.

    Args:
        id (int): User ID.
    Returns:
        (Admins): The admin with the given User ID
    '''
    return Admins.query.get(int(id))


class Episodes(db.Model):
    '''
    SQLAlchemy model for the episodes table in the db.
    '''

    id = db.Column(db.Integer,
                   primary_key=True)

    ep_num = db.Column(db.Integer,
                       unique=True,
                       nullable=False)

    date = db.Column(db.Date,
                     nullable=False)

    num_items = db.Column(db.Integer)

    theme = db.Column(db.String(50),
                      unique=False,
                      nullable=True)

    results = db.relationship('Results',
                              backref='episode',
                              lazy='dynamic')

    def __init__(self, ep_num, date, num_items, theme):
        '''
        Initialize an Episode object.
        '''
        self.ep_num = ep_num
        self.date = date
        self.num_items = num_items
        # if theme is blank, convert to None<->Null
        if theme == '':
            self.theme = None
        else:
            self.theme = theme

    def __repr__(self):
        '''
        Print formatting.
        '''
        return f'Ep {self.ep_num} - {self.date}: {self.num_items} items'


class Participants(db.Model):
    '''
    SQLAlchemy model for the participants table in the db.
    '''
    id = db.Column(db.Integer,
                   primary_key=True)

    name = db.Column(db.String(80),
                     unique=True,
                     nullable=False)

    date_created = db.Column(db.Date,
                             nullable=False,
                             default=datetime.now())

    is_rogue = db.Column(db.Boolean,
                         nullable=False,
                         default=False)

    rogue_start_date = db.Column(db.Date,
                                 nullable=True)

    rogue_end_date = db.Column(db.Date,
                               nullable=True)

    results = db.relationship('Results',
                              backref='participant',
                              lazy='dynamic')

    def __init__(self, name, is_rogue=False,
                 rogue_start_date=None,
                 rogue_end_date=None):
        '''
        Initialize a Participant object.
        '''
        # Automatically properly capitalize names for consistency.
        self.name = name.title()
        self.is_rogue = is_rogue
        self.rogue_start_date = rogue_start_date
        self.rogue_end_date = rogue_end_date

    def __repr__(self):
        '''
        Print Formatting.
        '''
        if self.is_rogue:
            rogue_statement = 'Rogue'
        else:
            rogue_statement = 'Guest'
        return f'{self.name}: {rogue_statement}'


class Results(db.Model):
    '''
    SQLAlchemy model for the results table in the db.
    '''
    id = db.Column(db.Integer,
                   primary_key=True)

    episode_id = db.Column(db.Integer,
                           db.ForeignKey('episodes.id'),
                           nullable=False)

    participant_id = db.Column(db.Integer,
                               db.ForeignKey('participants.id'),
                               nullable=False)

    is_correct = db.Column(db.Boolean,
                           nullable=True)

    is_absent = db.Column(db.Boolean,
                          nullable=False)

    is_presenter = db.Column(db.Boolean,
                             nullable=False,
                             default=0)

    def __init__(self, episode_id, rogue_id, is_correct):
        '''
        Initialize a Result object.
        '''
        self.episode_id = episode_id
        self.participant_id = rogue_id
        self.is_correct = None
        self.is_absent = 0

        if is_correct == 'correct':
            self.is_correct = 1
        elif is_correct == 'incorrect':
            self.is_correct = 0
        elif is_correct == 'absent':
            self.is_correct = None
            self.is_absent = 1
        elif is_correct == 'presenter':
            self.is_correct = None
            self.is_presenter = 1

    def __repr__(self):
        '''
        Print Formatting.
        '''
        return f'rogue_id={self.participant_id}|is_correct={self.is_correct}'


class Admins(db.Model):
    '''
    SQLAlchemy model for the admins table in the db.
    '''
    id = db.Column(db.Integer,
                   primary_key=True)

    username = db.Column(db.String(80),
                         nullable=False)

    password = db.Column(db.String(80),
                         nullable=False)

    firstname = db.Column(db.String(80),
                          nullable=True)

    lastname = db.Column(db.String(80),
                         nullable=True)

    def __init__(self, username, password,
                 firstname=False, lastname=False,
                 encrypted=False):
        '''
        Initialize an Admin object.
        '''
        from .extensions import encrypt
        self.username = username
        if firstname:
            self.firstname = firstname
        if lastname:
            self.lastname = lastname
        if not encrypted:
            self.password = encrypt(password)
        elif encrypted:
            self.password = password

    def __repr__(self):
        '''
        Print Formatting.
        '''
        return f'Admin {self.username}'

    def is_authenticated(self):
        '''
        Mandatory attribute to support SQLAlchemy. Returns True always as any
        admin in table is automatically authenticated.
        '''
        return True

    def is_active(self):
        '''
        Mandatory attribute to support SQLAlchemy. Returns True always as any
        admin in table is automatically active.
        '''
        return True

    def is_anonymous(self):
        '''
        Mandatory attribute to support SQLAlchemy. Returns False always as any
        admin in table is automatically not anonymous.
        '''
        return False

    def get_id(self):
        '''
        Mandatory attribute to support SQLAlchemy. Returns the id of the given
        admin.
        '''
        return self.id
