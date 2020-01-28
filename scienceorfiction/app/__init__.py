# App initialization

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .extensions import database_ready, init_db, login_manager
from .models import db
from .routes import addRoutes

csrf = CSRFProtect()


def create_app():
    '''
    Creates a Flask App as per the App Factory Pattern

    Args:
        None
    Returns:
        Flask App
    '''

    app = Flask(__name__, instance_relative_config=False,
                template_folder='templates',
                static_folder='static')
    app.config.from_object('config.Config')

    with app.app_context():

        db.init_app(app)
        csrf.init_app(app)

        login_manager.init_app(app)
        addRoutes(app)

        if database_ready(db, app):
            db.create_all()
            db.session.commit()
            init_db(db)

        return app
