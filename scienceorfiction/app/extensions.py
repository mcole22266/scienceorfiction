from os import environ
from time import sleep
from hashlib import sha256

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'admin_login'


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
    from .models import Participants
    for rogue in ['Steve', 'Bob', 'Jay', 'Evan', 'Cara']:
        present = Participants.query.filter_by(name=rogue).first()
        if not present:
            participant = Participants(rogue, is_rogue=True)
            db.session.add(participant)
    db.session.commit()


def updateRogueTable(roguename, correct):
    from .models import Participants
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
    from .models import Results, Episodes
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
    from .models import Participants
    rogues = Participants.query.filter_by(
        is_rogue=True).order_by(
            Participants.name).all()

    if onlyNames:
        for i, rogue in enumerate(rogues):
            rogues[i] = rogue.name

    return rogues


def getGuests():
    from .models import Participants
    guests = Participants.query.filter_by(
        is_rogue=False).order_by(
            Participants.name).all()

    return guests


def check_authentication(username, password):
    from .models import Admins
    admin = Admins.query.filter_by(username=username).first()
    if admin:
        if admin.password == encrypt(password):
            return True
    return False


def encrypt(string):
    string = string.encode()
    return sha256(string).hexdigest()


def generate_secret_code():
    from string import ascii_letters
    from random import choice
    secret_code = [choice(ascii_letters) for _ in range(10)]
    secret_code = ''.join(secret_code)
    return secret_code


def email_secret_code(secret_code, mail):
    # logic to send email
    return secret_code
