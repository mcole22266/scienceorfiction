from threading import Thread
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_login import login_required, current_user, login_user, logout_user

from .forms import (AddEntryForm, AdminLoginForm, AdminCreateForm,
                    AdminAuthenticateForm)
from .models import db, Episodes, Results, Admins
from .extensions import (database_ready, init_db, login_manager,
                         getRogues, getGuests,
                         updateRogueTable, checkSweep,
                         check_authentication, email_secret_code,
                         generate_secret_code, encrypt)


csrf = CSRFProtect()
secret_code = generate_secret_code()


def create_app():
    app = Flask(__name__, instance_relative_config=False,
                template_folder='templates',
                static_folder='static')
    app.config.from_object('config.Config')

    with app.app_context():

        db.init_app(app)
        csrf.init_app(app)

        login_manager.init_app(app)

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
                return redirect(url_for('admin'))

            # GET
            return render_template('addEntry.html',
                                   title='Admin - Add Entry',
                                   form=form,
                                   rogues=getRogues(),
                                   guests=getGuests()
                                   )

        @app.route('/admin/login', methods=['GET', 'POST'])
        def admin_login():
            if current_user.is_authenticated:
                return redirect(url_for('admin'))
            form = AdminLoginForm()

            # POST
            if form.validate_on_submit():
                username = request.form['username']
                password = request.form['password']
                if check_authentication(username, password):
                    admin = Admins.query.filter_by(username=username).first()
                    login_user(admin)
                    return redirect(url_for('admin'))
                else:
                    flash('Username and/or Password incorrect')
                    return redirect(url_for('admin_login'))

            # GET
            return render_template('adminLogin.html',
                                   title='Admin - Login',
                                   form=form)

        @app.route('/admin/create', methods=['GET', 'POST'])
        def admin_create():
            if current_user.is_authenticated:
                return redirect(url_for('admin'))
            form = AdminCreateForm()

            # POST
            if form.validate_on_submit():
                username = request.form['username']
                password = encrypt(request.form['password'])
                return redirect(url_for('admin_authenticate',
                                        username=username,
                                        password=password))

            # GET
            return render_template('adminCreate.html',
                                   title='Admin - Create',
                                   form=form)

        @app.route('/admin/authenticate', methods=['GET', 'POST'])
        def admin_authenticate():
            if current_user.is_authenticated:
                return redirect(url_for('admin'))
            form = AdminAuthenticateForm()
            username = request.args.get('username')
            app.logger.info(username)
            password = request.args.get('password')
            app.logger.info(password)

            # POST
            if request.method == 'POST':
                secret_code_form = request.form['secret_code']
                if secret_code_form == secret_code:
                    username = request.form['username']
                    password = request.form['password']
                    admin = Admins(username, password, encrypted=True)
                    db.session.add(admin)
                    db.session.commit()
                    login_user(admin)
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('admin_authenticate'))

            # GET
            thread = Thread(target=email_secret_code, args=[secret_code])
            thread.start()
            return render_template('adminAuthenticate.html',
                                   title='Admin - Authenticate',
                                   username=username,
                                   password=password,
                                   form=form)

        @app.route('/logout')
        @login_required
        def logout():
            logout_user()
            return redirect(url_for('admin'))

        return app
