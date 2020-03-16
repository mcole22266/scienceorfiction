# __init__.py
# Created by: Michael Cole
# Updated by: [Michael Cole]
# --------------------------
# App initialization

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from .extensions import database_ready, init_app, init_db, login_manager
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
    # Load environment variables into the app
    app.config.from_object('config.Config')

    with app.app_context():

        # Initialize app with SQLAlchemy
        db.init_app(app)
        # Initialize app with CSRF protection from WTForms
        csrf.init_app(app)

        # Initialize app with login manage from Flask_Logins
        login_manager.init_app(app)
        # Initialize app with defined routes
        addRoutes(app)

        if database_ready(db, app):
            db.create_all()      # Create and populate all tables
            db.session.commit()
            init_db(db)          # Initialize db with test data
            init_app(app)        # Initialize app with prepared graphs

        return app
