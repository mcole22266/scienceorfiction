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


def init_db(db):
    '''
    Initializes database with temporary data if data
    is not already present.
    Args:
        db (SQLAlchemy): db object from .models
    Returns:
        None
    '''
    for rogue in testdata.getRogues():
        present = getParticipant(rogue)
        if not present:
            addParticipant(db, rogue, is_rogue=True)
    for admin in testdata.getAdmins():
        present = getAdmins(admin[0])
        if not present:
            addAdmins(db, admin[0], admin[1])
    for episode in testdata.getEpisodes():
        present = getEpisode(episode['ep_num'])
        if not present:
            addEpisode(db, episode['ep_num'], episode['ep_date'],
                       episode['num_items'], episode['theme'],
                       episode['rogues'])
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
    episodes = Episodes.query.all()
    themes = set([episode.theme for episode in episodes if episode.theme])
    return sorted(list(themes))


def check_authentication(username, password):
    admin = getAdmins(username)
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


def addParticipant(db, name, is_rogue=False, commit=False):
    from .models import Participants
    participant = Participants(name, is_rogue)
    db.session.add(participant)
    if commit:
        db.session.commit()
    return participant


def getParticipant(name):
    from .models import Participants
    participant = Participants.query.filter_by(name=name).first()
    return participant


def addResult(db, episode_id, rogue_id, is_correct, commit=False):
    from .models import Results
    result = Results(episode_id, rogue_id, is_correct)
    db.session.add(result)
    if commit:
        db.session.commit()
    return result


def getResults(episode_id=False, participant_id=False,
               daterange=False, theme=False):
    from .models import Results, Episodes
    if episode_id and participant_id:
        # get specific results for this participant on this episode
        return Results.query.filter_by(episode_id=episode_id,
                                       participant_id=participant_id).first()
    elif episode_id and not participant_id:
        # get all results for this specific episode
        results = Results.query.filter_by(episode_id=episode_id).all()
    elif not episode_id and participant_id:
        # get all results for this specific participant
        results = Results.query.filter_by(participant_id=participant_id).all()
    else:
        return None
    if daterange:
        startdate, enddate = daterange  # daterange is a tuple
        for result in results:
            episode = Episodes.query.filter_by(id=result.episode_id).first()
            date = episode.date
            if date < startdate or date < enddate:
                results.remove(result)
    if theme:
        for result in results:
            episode = Episodes.query.filter_by(id=result.episode_id).first()
            ep_theme = episode.theme
            if ep_theme != theme:
                results.remove(result)
    return results


def addEpisode(db, ep_num, date, num_items, theme, participant_results,
               commit=False):
    from .models import Episodes
    episode = Episodes(ep_num, date, num_items, theme)
    results = []
    db.session.add(episode)
    for participant, correct in participant_results:
        episode_id = getEpisode(ep_num).id
        rogue_id = getParticipant(participant).id
        results.append(addResult(db, episode_id, rogue_id, correct))
    if commit:
        db.session.commit
    return episode, results


def getEpisode(ep_num=False, ep_id=False):
    from .models import Episodes
    if ep_num:
        episode = Episodes.query.filter_by(ep_num=ep_num).first()
    elif ep_id:
        episode = Episodes.query.filter_by(id=ep_id).first()
    return episode


def getAllEpisodes(daterange=False):
    from .models import Episodes
    if daterange:
        startdate, enddate = daterange  # daterange is a tuple
        episodes = Episodes.query.filter(
            Episodes.date.between(startdate, enddate)).all()
    else:
        episodes = Episodes.query.all()
    return episodes


def addAdmins(db, username, password, encrypted=False, commit=False):
    from .models import Admins
    admin = Admins(username, password, encrypted)
    db.session.add(admin)
    if commit:
        db.session.commit()
    return admin


def getAdmins(username):
    from .models import Admins
    admin = Admins.query.filter_by(username=username).first()
    return admin
