from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required

from .extensions import (database_ready, init_db,
                         getRogues, getGuests,
                         updateRogueTable, checkSweep)
from .forms import AddEntryForm
from .models import db, Episodes, Results


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, instance_relative_config=False,
                template_folder='templates',
                static_folder='static')
    app.config.from_object('config.Config')

    with app.app_context():

        db.init_app(app)
        csrf.init_app(app)

        if database_ready(db, app):
            db.create_all()
            db.session.commit()
            init_db(db)

        @app.route('/')
        def index():
            return 'Hello World'

        @app.route('/admin', methods=['GET', 'POST'])
        @login_required
        def admin():
            form = AddEntryForm()

            # POST
            if form.validate_on_submit():
                rogues = getRogues(onlyNames=True)
                date = request.form['date']
                ep_num = request.form['ep_num']
                num_items = request.form['num_items']
                episode = Episodes(date, ep_num, num_items)
                db.session.add(episode)
                db.session.commit()
                episode = Episodes.query.filter_by(ep_num=ep_num).first()
                for key in request.form.keys():
                    if key in rogues:
                        correct = request.form[key]
                        rogue_id = updateRogueTable(key, correct)
                        if rogue_id:
                            results = Results(episode.id, rogue_id, correct)
                            db.session.add(results)
                    db.session.commit()
                checkSweep(db, episode.id, app)
                return redirect(url_for('update'))

            # GET
            return render_template('addEntry.html',
                                   title='TEST - Add Entry',
                                   form=form,
                                   rogues=getRogues(),
                                   guests=getGuests()
                                   )
        return app

        @app.route('/admin/login')
        def admin_login():
            return 'admin login'

        @app.route('/admin/create')
        def admin_create():
            return 'admin create'
