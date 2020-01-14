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
    from .models import Participants, Episodes, Admins
    for rogue in ['Steve', 'Bob', 'Jay', 'Evan', 'Cara']:
        present = Participants.query.filter_by(name=rogue).first()
        if not present:
            participant = Participants(rogue, is_rogue=True)
            db.session.add(participant)
    for i, theme in enumerate(['Bears', 'Beets', 'Battlestar Gallactica',
                               'Star Wars', 'Star Trek', 'Science',
                               'Nanomachines']):
        present = Episodes.query.filter_by(ep_num=i).first()
        if not present:
            episode = Episodes('2020-01-01', i, 3, theme)
            db.session.add(episode)
    present = Admins.query.filter_by(username='admin').first()
    if not present:
        admin = Admins('admin', 'adminpass')
        db.session.add(admin)
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
        if correct == 'presenter':
            rogue.presented += 1
            rogue.present += 1
        return rogue.id


def checkSweep(db, episode_id, app):
    from .models import Results, Episodes
    results = Results.query.filter_by(episode_id=episode_id).all()
    results = [result.correct for result in results]
    if len(set(results)) == 1:
        # it's a sweep!
        episode = Episodes.query.filter_by(id=episode_id).first()
        if results[0] is False:
            episode.sweep = 'presenter sweep'
        else:
            episode.sweep = 'player sweep'
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


def getThemes():
    from .models import Episodes
    # themes = db.session.query(Episodes.theme).distinct().isnot(None)
    # themes = [theme[0] for theme in themes]
    episodes = Episodes.query.filter(Episodes.theme != None).order_by(
        Episodes.theme).all()

    themes = set([episode.theme for episode in episodes])
    return sorted(list(themes))


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


def email_secret_code(secret_code):
    import yagmail
    GMAIL_USERNAME = environ['GMAIL_USERNAME']
    GMAIL_PASSWORD = environ['GMAIL_PASSWORD']
    yag = yagmail.SMTP(GMAIL_USERNAME, GMAIL_PASSWORD)
    subject = 'Secret Code Generation Bot'
    contents = f'''
-- AUTOMATED MESSAGE --

Secret Code: {secret_code}

With Love,
The Bot'''
    yag.send(GMAIL_USERNAME, subject, contents)
