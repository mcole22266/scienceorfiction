from flask import Flask, render_template

from .extensions import database_ready, getRogues, getGuests
from .forms import AddEntryForm


def create_app():
    app = Flask(__name__, instance_relative_config=False,
                template_folder='templates',
                static_folder='static')
    app.config.from_object('config.Config')

    with app.app_context():

        from .models import db
        db.init_app(app)

        from flask_wtf import CSRFProtect
        CSRFProtect(app)

        if database_ready(db, app):
            db.create_all()
            db.session.commit()

        @app.route('/')
        def index():
            return 'Hello World'

        @app.route('/test/update', methods=['GET', 'POST'])
        def update():
            form = AddEntryForm()
            return render_template('addEntry.html',
                                   title='TEST - Add Entry',
                                   form=form,
                                   rogues=getRogues(),
                                   guests=getGuests()
                                   )

        return app
