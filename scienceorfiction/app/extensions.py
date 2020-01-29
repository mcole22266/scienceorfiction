# Contains several different helper functions

from hashlib import sha256
from os import environ
from time import sleep

from flask_login import LoginManager

from .testing import testdata

login_manager = LoginManager()
login_manager.login_view = 'admin_login'


def database_ready(db, app):
    '''
    Checks for a database connection at intervals given
    by the env file up to an interval limit given by
    the env file.

    Args:
        db (SQLAlchemy): db object from .models
        app (Flask): app object from init
    Returns:
        (bool): True upon db connection success
                False if connection times out
    '''

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


def init_db(db, app):
    '''
    Initializes database with temporary data if data
    is not already present.
    Args:
        db (SQLAlchemy): db object from .models
    Returns:
        None
    '''
    from .models import Participants, Episodes, Admins, Results
    for rogue in testdata.getRogues():
        present = Participants.query.filter_by(name=rogue).first()
        if not present:
            participant = Participants(rogue, is_rogue=True)
            db.session.add(participant)
    for admin in testdata.getAdmins():
        present = Admins.query.filter_by(username=admin[0]).first()
        if not present:
            administrator = Admins(admin[0], admin[1])
            db.session.add(administrator)
    for episode in testdata.getEpisodes():
        present = Episodes.query.filter_by(ep_num=episode['ep_num']).first()
        if not present:
            ep = Episodes(episode['ep_num'], episode['ep_date'],
                          episode['num_items'], episode['theme'])
            db.session.add(ep)
            for rogue in testdata.getRogues():
                for rogueResult in episode['rogues']:
                    if rogueResult[0] == rogue:
                        correct = rogueResult[1]
                rogue_id = updateRogueTable(rogue, correct)
                results = Results(ep.id, rogue_id, correct)
                db.session.add(results)
            checkSweep(db, ep.id, app)
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
    if 1 in results and 0 in results:
        # no sweep
        pass
    else:
        # it's a sweep!
        episode = Episodes.query.filter_by(id=episode_id).first()
        if 1 in results:
            episode.sweep = 'player sweep'
        else:
            episode.sweep = 'presenter sweep'
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
