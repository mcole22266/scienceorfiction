from flask import Flask

from .extensions import database_ready


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():

        from .models import db
        db.init_app(app)

        if database_ready(db, app):
            db.create_all()
            db.session.commit()

        @app.route('/')
        def index():
            return 'Hello World'

        return app
