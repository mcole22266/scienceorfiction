# extensions.py
# Created by: Michael Cole
# Updated by: [Michael Cole]
# ----------------------------
# Contains several different helper functions to support the application
# by providing ease of use functionality.

from datetime import date, datetime
from hashlib import sha256
from os import environ, makedirs, path
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
    rogues = testdata.getRoguesRandomized()
    for rogue in rogues:
        roguename, accuracy, start, end = rogue
        present = getParticipant(roguename)
        if not present:
            addParticipant(db, roguename, is_rogue=True,
                           rogue_start_date=start,
                           rogue_end_date=end)
    for admin in testdata.getAdmins():
        present = getAdmin(admin[0])
        if not present:
            addAdmin(db, admin[0], admin[1])
    for episode in testdata.getEpisodes(rogues):
        present = getEpisode(episode['ep_num'])
        if not present:
            addEpisode(db, episode['ep_num'], episode['ep_date'],
                       episode['num_items'], episode['theme'],
                       episode['guests'], episode['rogues'])
    db.session.commit()


def init_app(app):
    '''
    Initializes the app with custom initializers.

    Args:
        app (Flask): app from Flask
    Returns:
        None
    '''
    init_graphs(app)


def init_graphs(app):
    '''
    Initializes the application with the necessary graphs for users.
    (Designed to be used upon app startup).

    Args:
        app(Flask): app from Flask
    Returns:
        None
    '''
    from .graphs import buildAllGraphs
    # Create bokeh folder if doesn't already exist
    app.logger.info('Checking if bokeh folder exists')
    if not path.exists('/scienceorfiction/app/templates/bokeh'):
        app.logger.info('No bokeh folder found, creating folder')
        makedirs('/scienceorfiction/app/templates/bokeh')
    else:
        app.logger.info('bokeh folder found')

    app.logger.info('Building all graphs')
    graphTypes = ['overallAccuracy', 'accuracyOverTime', 'sweeps']
    graphYears = getYears()
    graphYears.append('overall')
    buildAllGraphs(graphTypes, graphYears)
    app.logger.info('All graphs built')


def getRogues(onlyNames=False, current_date=False, daterange=False):
    '''
    Support function used to retrieve rogues based on certain parameters.

    Args:
        onlyNames (bool) - optional: Set to True if only rogue names are
            desired.
        current_date (bool) - optional: Set to True if only rogues who
            are currently active are desired.
        daterange (list or tuple) - optional: Pass a start and stop date
            to retrieve only rogues who were active within a date window.
    Returns:
        (list): List of rogues who meet the specified paramters
    '''
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


def getGuests(onlyNames=False, daterange=False):
    '''
    Support function used to retrieve guests based on certain parameters.

    Args:
        onlyNames (bool) - optional: Set to True if only guest names are
            desired.
        daterange (list or tuple) - optional: Pass a start and stop date
            to retrieve only guests who were active within a date window.
    Returns:
        (list): List of guests who meet the specified paramters
    '''
    from .models import Participants
    guests = Participants.query.filter_by(
        is_rogue=False).order_by(
            Participants.name).all()

    if daterange:
        for guest in guests[:]:
            results = getResults(participant_id=guest.id)
            dates = []
            for result in results:
                ep = getEpisode(ep_id=result.episode_id)
                dates.append(ep.date)
            present = False
            for d in dates:
                if d >= daterange[0] and d <= daterange[1]:
                    present = True
                    break
            if not present:
                guests.remove(guest)

    if onlyNames:
        for i, guest in enumerate(guests):
            guests[i] = guest.name

    return guests


def getThemes():
    '''
    Support function used to retrieve all themes from database.

    Returns:
        (list): List of all themes.
    '''
    from .models import Episodes
    episodes = Episodes.query.with_entities(Episodes.theme).order_by(
               Episodes.theme).distinct()
    episodes = [episode[0] for episode in episodes]
    return episodes


def getYears(desc=False):
    '''
    Support function used to retrieve all years from database.

    Args:
        desc (bool) - optional: If True, data is sorted in reverse order.
    Returns:
        (list): List of all years in db.
    '''
    from .models import Episodes
    episodes = Episodes.query.all()
    dates = sorted(list(set([str(episode.date.year) for episode in episodes])))
    if desc:
        dates = reversed(dates)
    return dates


def check_authentication(username, password):
    '''
    Support function used to verify a username/password combo.

    Args:
        username (str): Username to verify.
        password (str): The unencrypted password to test.
    Returns:
        (bool): Returns True is authenticated.
    '''
    admin = getAdmin(username)
    if admin:
        if admin.password == encrypt(password):
            return True
    return False


def encrypt(string):
    '''
    Support function used to encrypt a string.

    Args:
        string (str): String to encrypt.
    Returns:
        (str): encoded version of given string.
    '''
    string = string.encode()
    return sha256(string).hexdigest()


def generate_secret_code():
    '''
    Support function to generate a secret code.

    Returns:
        (str): Secret Code.
    '''
    from string import ascii_letters
    from random import choice
    secret_code = [choice(ascii_letters) for _ in range(10)]
    secret_code = ''.join(secret_code)
    return secret_code


def email_secret_code(secret_code):
    '''
    Support function specifically used to email the secret code
    to the username given in the environment variables.

    Args:
        secret_code (str): Secret code to email.
    Returns:
        None
    '''
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
    '''
    Support function used to add a new participant to the db.

    Args:
        db (SQLAlchemy db): db object
        name (str): Particpant Name
        is_rogue (bool) - optional: Set to True if particpant is a rogue.
        rogue_start_date (date) - optional: Should be set if is_rogue==True.
            Date in which the rogue begins.
        rogue_end_date (date) - optional: Set only if rogue no longer is an
            active rogue.
        commit (bool) - optional: Set to True to have the function commit the
            changes.
    Returns:
        (Participants): db.Model from the participants table in the db.
    '''
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
    '''
    Support function used to retrieve a particpant from the db.

    Args:
        name (str): Unique name to use in order to retrieve the participant.
    Returns:
        (Participants): db.Model from the participants table in the db.
    '''
    from .models import Participants
    name = name.title()
    participant = Participants.query.filter_by(name=name).first()
    return participant


def getAllParticipants():
    '''
    Support function used to retreive all participants from the db.

    Returns:
        (list): List of all participants in the db.
    '''
    from .models import Participants
    participants = Participants.query.all()
    return participants


def addResult(db, episode_id, rogue_id, is_correct, commit=False):
    '''
    Support function used to add a new result to the db.

    Args:
        db (SQLAlchemy db): db object
        episode_id (int): Unique Episode ID
        rogue_id (int): Unique Rogue ID
        is_correct (bool): True/False indicating rogue result.
        commit (bool) - optional: Set to True to have the function commit the
            changes.
    Returns:
        (Results): db.Model from the results table in the db.
    '''
    from .models import Results
    result = Results(episode_id, rogue_id, is_correct)
    db.session.add(result)
    if commit:
        db.session.commit()
    return result


def getResults(episode_id=False, participant_id=False,
               daterange=False, theme=False):
    '''
    Support function to retrieve data from the results table based on given
    parameters.

    Args:
        episode_id (int) - optional: Set to retrieve all results for a single
            episode.
        participant_id (int) - optional: Set to retrieve all results for a
            single participant.
        daterange (list[date]) - optional: Set to retrieve all results within
            a date window.
        theme (str) - optional: Set to retrieve all results for a given theme.
    Returns:
        (list): List of all results in the table that match the given
            parameters.
    '''
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
    '''
    Support function to retrieve all results from the results table in the db.

    Returns:
        (list): List of all results in the db.
    '''
    from .models import Results
    results = Results.query.all()
    return results


def addEpisode(db, ep_num, date, num_items, theme, guests, participant_results,
               commit=False):
    '''
    Support function used to add a new episode to the db.

    Args:
        db (SQLAlchemy db): db object.
        episode_num (int): Unique Episode Number.
        date (date): Unique date for the episode.
        num_items (int): Number of items in the Science or Fiction.
        theme (str): Theme for the episode's Science or Fiction.
        guests (list[str]): List of guests who participated in the episode. If
            they do not currently exist in the db, they are added.
        participant_results (list[tuple(Participants,str)]): A list of tuples
            that give a participant as well as the result.
        commit (bool) - optional: Set to True to have the function commit the
            changes.
    Returns:
        (Results): db.Model from the episodes table in the db.
    '''
    from .models import Episodes
    results = []
    episode = Episodes(ep_num, date, num_items, theme)
    db.session.add(episode)
    episode = getEpisode(ep_num=ep_num)
    for name in guests:
        present = getParticipant(name)
        if not present:
            addParticipant(db, name)
    for (participant, correct) in participant_results:
        rogue = getParticipant(participant)
        results.append(addResult(db, episode.id, rogue.id, correct))
    if commit:
        db.session.commit()
    return episode, results


def getEpisode(ep_num=False, ep_id=False):
    '''
    Support function to retrieve an episode from the db.

    Args:
        ep_num (int) - optional: Set to retrieve the episode by the
            episode number.
        ep_id (int) - optional: Set to retreive the episode by the
            episode id.

    Returns:
        (db.Episodes): The desired episode based on the parameters.
    '''
    from .models import Episodes
    if ep_num:
        episode = Episodes.query.filter_by(ep_num=ep_num).first()
    elif ep_id:
        episode = Episodes.query.filter_by(id=ep_id).first()
    return episode


def getAllEpisodes(daterange=False, desc=False):
    '''
    Support function to retrieve all episodes in the database that
    fit within certain parameters. Call function with no arguments
    to simply return all episodes.

    Args:
        daterange (list[date]) - optional: Set to only retrieve episodes
            that fall within the given date range.
        desc (bool) - optional: Set to True to have the data returned
            sorted in descending order.

    Returns:
        (list): List of all episodes that fit the given criteria.
    '''
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


def addAdmin(db, username, password,
             firstname=False, lastname=False,
             encrypted=False, commit=False):
    '''
    Support function used to add a new admin to the db.

    Args:
        db (SQLAlchemy db): db object.
        username (str): Admin username.
        password (str): Chosen password. If set to an already encrypted
            password, encrypted arg should be set to True.
        firstname (str) - optional: Admin first name.
        lastname (str) - optional: Admin last name.
        encrypted (bool) - optional: Set to true if the given password has
            already been encrypted.
        commit (bool) - optional: Set to True to have the function commit the
            changes.
    Returns:
        (Results): db.Model from the admins table in the db.
    '''
    from .models import Admins
    admin = Admins(username, password, firstname, lastname, encrypted)
    db.session.add(admin)
    if commit:
        db.session.commit()
    return admin


def getAdmin(username=False, all=False):
    '''
    Support function to retreive a single admin or all admins.

    Args:
        username (str) - optional: Retrieve a single admin based on username.
        all (bool) - optional: Set to True in order to retrieve all admins.
    Returns:
        (db.Admins): A single administrator
        (list): A list of all administrators
    '''
    from .models import Admins
    if username:
        admin = Admins.query.filter_by(username=username).first()
        return admin
    if all:
        admins = Admins.query.all()
        return admins


def getUserFriendlyRogues(db):
    '''
    Support function to retrieve specific information from multiple tables
    regarding Rogues.

    Args:
        db (SQLAlchemy db): db object.
    Returns:
        (list): List of all pertinent information regarding rogues.
    '''
    data = db.session.execute('''
    SELECT
        name, rogue_start_date, rogue_end_date,
        SUM(is_correct) AS correct,
        COUNT(is_correct)-SUM(is_correct) AS incorrect
    FROM
        participants, results
    WHERE
        participants.id = participant_id AND
        is_rogue=1
    GROUP BY
        participants.id
    ORDER BY
        rogue_start_date
    ''')
    return data.fetchall()


def getUserFriendlyGuests(db):
    '''
    Support function to retrieve specific information from multiple tables
    regarding Guests.

    Args:
        db (SQLAlchemy db): db object.
    Returns:
        (list): List of all pertinent information regarding guests.
    '''
    data = db.session.execute('''
    SELECT
        name,
        count(is_correct) AS num_appearances,
        SUM(is_correct) AS correct,
        COUNT(is_correct)-SUM(is_correct) AS incorrect
    FROM participants, results
    WHERE
        participants.id = participant_id AND
        is_rogue=0
    GROUP BY
        participants.id
    ORDER BY
        num_appearances DESC
    ''')
    return data.fetchall()


def getUserFriendlyEpisodeData(db):
    '''
    Support function to retrieve specific information from multiple tables
    regarding Episodes.

    Args:
        db (SQLAlchemy db): db object.
    Returns:
        (list): List of all pertinent information regarding episodes.
    '''
    ep_data = db.session.execute('''
    SELECT
        ep_num, date, num_items, theme,
        name AS presenter
    FROM
        episodes AS ep
    JOIN
        results AS res ON ep.id=res.episode_id
    JOIN
        participants AS p on res.participant_id=p.id
    WHERE
        res.is_presenter=1
    ORDER BY
        ep_num DESC
    ''')
    return ep_data.fetchall()


def getUserFriendlyEpisodeSums(db):
    '''
    Support function to retrieve specific information from multiple tables
    regarding totaling information.

    Args:
        db (SQLAlchemy db): db object.
    Returns:
        (list): List of all pertinent information regarding totals.
    '''
    sum_data = db.session.execute('''
    SELECT
        ep.ep_num,
        SUM(is_correct) AS correct,
        COUNT(is_correct)-SUM(is_correct) AS incorrect
    FROM
        results AS res
    JOIN
        episodes AS ep ON res.episode_id=ep.id
    GROUP BY
        episode_id
    ORDER BY
        ep.ep_num DESC
    ''')

    return sum_data.fetchall()
