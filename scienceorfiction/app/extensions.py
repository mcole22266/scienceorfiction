# Contains several different helper functions

from hashlib import sha256
from os import environ, path, makedirs
from time import sleep
from datetime import date, datetime

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
    rogues = testdata.getRoguesRandomized()
    for rogue in rogues:
        roguename, accuracy, start, end = rogue
        present = getParticipant(roguename)
        if not present:
            addParticipant(db, roguename, is_rogue=True,
                           rogue_start_date=start,
                           rogue_end_date=end)
    for admin in testdata.getAdmins():
        present = getAdmins(admin[0])
        if not present:
            addAdmins(db, admin[0], admin[1])
    for episode in testdata.getEpisodes(rogues):
        present = getEpisode(episode['ep_num'])
        if not present:
            addEpisode(db, episode['ep_num'], episode['ep_date'],
                       episode['num_items'], episode['theme'],
                       episode['rogues'])
    db.session.commit()


def init_app(app):
    '''
    Initializes the app.
    Args:
        app (Flask): app from Flask
    Returns:
        None
    '''
    app.logger.info('Checking if bokeh folder exists')
    if not path.exists('/scienceorfiction/app/templates/bokeh'):
        app.logger.info('No bokeh folder found, creating folder')
        makedirs('/scienceorfiction/app/templates/bokeh')
    else:
        app.logger.info('bokeh folder found')


def getRogues(onlyNames=False, current_date=False, daterange=False):
    '''current arg is passed a date'''
    from .models import Participants
    rogues = Participants.query.filter_by(
        is_rogue=True).order_by(
            Participants.name).all()

    if current_date:
        for rogue in rogues[:]:
            if not rogue.rogue_end_date:
                end_date = date.today()
            else:
                end_date = rogue.rogue_end_date
            start_date = rogue.rogue_start_date
            if not start_date < current_date <= end_date:
                rogues.remove(rogue)

    if daterange:
        for rogue in rogues[:]:
            if not rogue.rogue_end_date:
                end_date = date.today()
            else:
                end_date = rogue.rogue_end_date
            start_date = rogue.rogue_start_date
            if start_date >= daterange[1] or end_date <= daterange[0]:
                rogues.remove(rogue)

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
    episodes = Episodes.query.with_entities(Episodes.theme).order_by(
               Episodes.theme).distinct()
    episodes = [episode[0] for episode in episodes]
    return episodes


def getYears():
    from .models import Episodes
    episodes = Episodes.query.all()
    dates = set([str(episode.date.year) for episode in episodes])
    return sorted(list(dates))


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


def addParticipant(db, name, is_rogue=False,
                   rogue_start_date=None, rogue_end_date=None,
                   commit=False):
    from .models import Participants
    # start and end dates need to be converted from date to datetime object
    # before being passed into the db
    if rogue_start_date:
        rogue_start_date = datetime(rogue_start_date.year,
                                    rogue_start_date.month,
                                    rogue_start_date.day)
    if rogue_end_date:
        rogue_end_date = datetime(rogue_end_date.year,
                                  rogue_end_date.month,
                                  rogue_end_date.day)
    present = getParticipant(name)
    if not present:
        participant = Participants(name, is_rogue,
                                   rogue_start_date=rogue_start_date,
                                   rogue_end_date=rogue_end_date)
        db.session.add(participant)
        if commit:
            db.session.commit()

        return participant

    return present


def getParticipant(name):
    from .models import Participants
    participant = Participants.query.filter_by(name=name).first()
    return participant


def getAllParticipants():
    from .models import Participants
    participants = Participants.query.all()
    return participants


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
        # get specific result for this participant on this episode
        return Results.query.filter_by(episode_id=episode_id,
                                       participant_id=participant_id).first()
    elif episode_id and not (participant_id or daterange or theme):
        # get all results for this specific episode
        return Results.query.filter_by(episode_id=episode_id).all()
    elif participant_id and not (episode_id or daterange or theme):
        # get all results for this specific participant
        return Results.query.filter_by(participant_id=participant_id).all()
    elif theme and not (episode_id or participant_id or daterange):
        # get all results for this specific theme
        return Results.query.join(Episodes).filter(
            Episodes.theme == theme).all()
    elif daterange and not (episode_id or participant_id or theme):
        # get all results within a date range
        return Results.query.join(Episodes).filter(
            Episodes.date.between(daterange[0], daterange[1])).all()
    elif participant_id and daterange and not theme:
        # get all results for this specific participant
        # over this period of time
        return Results.query.join(Episodes).filter(
            Episodes.date.between(daterange[0], daterange[1]),
            Results.participant_id == participant_id).all()
    elif participant_id and theme and not daterange:
        # get all results for this specific participant
        # for this theme
        return Results.query.join(Episodes).filter(
            Episodes.theme == theme,
            Results.participant_id == participant_id).all()
    elif participant_id and daterange and theme:
        # get all results for this specific participant
        # within this daterange and this theme
        return Results.query.join(Episodes).filter(
            Episodes.date.between(daterange[0], daterange[1]),
            Episodes.theme == theme,
            Results.participant_id == participant_id).all()


def getAllResults():
    from .models import Results
    results = Results.query.all()
    return results


def addEpisode(db, ep_num, date, num_items, theme, guests, participant_results,
               commit=False):
    from .models import Episodes
    episode = Episodes(ep_num, date, num_items, theme)
    for guest in guests:
        addParticipant(db, guest)
    results = []
    db.session.add(episode)
    for participant, correct in participant_results:
        episode_id = getEpisode(ep_num).id
        rogue_id = getParticipant(participant).id
        results.append(addResult(db, episode_id, rogue_id, correct))
    if commit:
        db.session.commit()
    return episode, results


def getEpisode(ep_num=False, ep_id=False):
    from .models import Episodes
    if ep_num:
        episode = Episodes.query.filter_by(ep_num=ep_num).first()
    elif ep_id:
        episode = Episodes.query.filter_by(id=ep_id).first()
    return episode


def getAllEpisodes(daterange=False, desc=False):
    from .models import Episodes
    if daterange and not desc:
        startdate, enddate = daterange  # daterange is a tuple
        episodes = Episodes.query.filter(
            Episodes.date.between(startdate, enddate)).all()
    elif daterange and desc:
        startdate, enddate = daterange  # daterange is a tuple
        episodes = Episodes.query.filter(
            Episodes.date.between(startdate, enddate)).order_by(
                Episodes.ep_num.desc()).all()
    elif not daterange and desc:
        episodes = Episodes.query.order_by(Episodes.ep_num.desc()).all()
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
