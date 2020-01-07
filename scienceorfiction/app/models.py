from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Episodes(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)

    date = db.Column(db.DateTime,
                     nullable=False)

    ep_num = db.Column(db.Integer,
                       unique=True,
                       nullable=False)

    num_items = db.Column(db.Integer)

    sweep = db.Column(db.String(10))  # offense, defense, no sweep

    results = relationship('Results')

    def __init__(self, date, ep_num, num_items, sweep):
        date = date,
        ep_num = ep_num
        num_items = num_items
        sweep = sweep

    def __repr__(self):
        if self.sweep != 'no sweep':
            sweep_statement = 'with a clean sweep for the {self.sweep}'
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
                             nullable=False)

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

    def __init__(self, name, date_created, is_rogue=False):
        self.name = name
        self.date_created = date_created
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

    episode = relationship('Episodes', back_populates='results')

    participant = db.Column(db.String(80),
                            unique=True,
                            nullable=False)

    correct = db.Column(db.Boolean,
                        nullable=False)

    def __init__(self, episode_id, participant, correct):
        self.episode_id = episode_id
        self.participant = participant
        self.correct = correct
