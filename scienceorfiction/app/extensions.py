from os import environ
from time import sleep
from hashlib import sha256

from .models import Participants, Results, Episodes


def database_ready(db, app):
    wait = int(environ['DB_WAIT_INITIAL'])
    wait_multiplier = int(environ['DB_WAIT_MULTIPLIER'])
    wait_max = int(environ['DB_WAIT_MAX'])

    success = False
    attemptNum = 1

    while wait < wait_max:

        try:
            app.logger.info('Attempting Database Connection')
            db.session.execute('SELECT 1')
            app.logger.info('Connection Success!')
            success = True
            break

        except Exception:
            app.logger.info(f'Connect {attemptNum} failed')
            app.logger.info(f'Waiting {wait} seconds')
            sleep(wait)
            wait *= wait_multiplier
            attemptNum += 1

    return success


def init_db(db):
    for rogue in ['Steve', 'Bob', 'Jay', 'Evan', 'Cara']:
        present = Participants.query.filter_by(name=rogue).first()
        if not present:
            participant = Participants(rogue, is_rogue=True)
            db.session.add(participant)
    db.session.commit()


def updateRogueTable(roguename, correct):
    if correct != 'NULL':
        rogue = Participants.query.filter_by(
            name=roguename).first()
        if correct == 'correct':
            rogue.wins += 1
            rogue.present += 1
        if correct == 'incorrect':
            rogue.losses += 1
            rogue.present += 1
        if correct == 'absent':
            rogue.absent += 1
        return rogue.id


def checkSweep(db, episode_id, app):
    results = Results.query.filter_by(episode_id=episode_id).all()
    results = [result.correct for result in results]
    if len(set(results)) == 1:
        # it's a sweep!
        episode = Episodes.query.filter_by(id=episode_id).first()
        if results[0] is False:
            episode.sweep = 'offense'
        else:
            episode.sweep = 'defense'
        db.session.commit()


def getRogues(onlyNames=False):
    rogues = Participants.query.filter_by(
        is_rogue=True).order_by(
            Participants.name).all()

    if onlyNames:
        for i, rogue in enumerate(rogues):
            rogues[i] = rogue.name

    return rogues


def getGuests():
    guests = Participants.query.filter_by(
        is_rogue=False).order_by(
            Participants.name).all()

    return guests


def encrypt(string):
    string = string.encode()
    return sha256(string).hexdigest()
