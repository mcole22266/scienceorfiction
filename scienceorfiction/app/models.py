from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Episodes(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)

    ep_num = db.Column(db.Integer,
                       unique=True,
                       nullable=False)

    date = db.Column(db.String(20),
                     nullable=False)

    num_items = db.Column(db.Integer)

    sweep = db.Column(db.String(10),
                      default='no sweep')  # offense, defense, no sweep

    results = db.relationship('Results',
                              backref='episode',
                              lazy='dynamic')

    def __init__(self, date, ep_num, num_items):
        self.date = date
        self.ep_num = ep_num
        self.num_items = num_items

    def __repr__(self):
        if self.sweep != 'no sweep':
            sweep_statement = f'with a clean sweep for the {self.sweep}'
        else:
            sweep_statement = 'without a clean sweep'
        return f'Ep {self.ep_num}-{self.date}: \
{self.num_items} items {sweep_statement}'


class Participants(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)

    name = db.Column(db.String(80),
                     unique=True,
                     nullable=False)

    date_created = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now())

    wins = db.Column(db.Integer,
                     nullable=False,
                     default=0)

    losses = db.Column(db.Integer,
                       nullable=False,
                       default=0)

    present = db.Column(db.Integer,
                        nullable=False,
                        default=0)

    absent = db.Column(db.Integer,
                       nullable=False,
                       default=0)

    is_rogue = db.Column(db.Boolean,
                         nullable=False,
                         default=False)

    results = db.relationship('Results',
                              backref='participant',
                              lazy='dynamic')

    def __init__(self, name, is_rogue=False):
        self.name = name
        self.is_rogue = is_rogue

    def __repr__(self):
        if self.is_rogue:
            rogue_statement = 'Rogue'
        else:
            rogue_statement = 'Temp'
        return f'{self.name} ({rogue_statement}): {self.wins}/{self.losses}'


class Results(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)

    episode_id = db.Column(db.Integer,
                           db.ForeignKey('episodes.id'))

    participant_id = db.Column(db.Integer,
                               db.ForeignKey('participants.id'))

    correct = db.Column(db.Boolean,
                        nullable=False)

    absent = db.Column(db.Boolean,
                       nullable=False)

    def __init__(self, episode_id, rogue_id, correct):
        self.episode_id = episode_id
        self.participant_id = rogue_id
        if correct == 'correct':
            self.correct = 1
        else:
            self.correct = 0
        if correct == 'absent':
            self.absent = 1
        else:
            self.absent = 0

    def __repr__(self):
        return f'rogue_id={self.participant_id}|correct={self.correct}'


class Admins(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)

    username = db.Column(db.String(80),
                         nullable=False)

    password = db.Column(db.String(80),
                         nullable=False)

    def __init__(self, username, password):
        from .extensions import encrypt
        self.username = username
        self.password = encrypt(password)

    def __repr__(self):
        return f'Admin {self.username}'
