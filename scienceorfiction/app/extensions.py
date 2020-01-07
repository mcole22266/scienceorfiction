from os import environ
from time import sleep

from .models import Participants


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


def getRogues():
    return Participants.query.filter_by(
        is_rogue=True).order_by(
            Participants.name).all()


def getGuests():
    return Participants.query.filter_by(
        is_rogue=False).order_by(
            Participants.name).all()
