# Contains all routing information (and lots of logic for now)

from threading import Thread

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .extensions import (check_authentication, checkSweep, email_secret_code,
                         encrypt, generate_secret_code, getGuests, getRogues,
                         getThemes, updateRogueTable)
from .forms import (AddEntryForm, AdminAuthenticateForm, AdminCreateForm,
                    AdminLoginForm)
from .models import Admins, Episodes, Results, db


secret_code = generate_secret_code()


def addRoutes(app):

    @app.route('/')
    def index():
        return 'Hello World'

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        form = AddEntryForm()

        # POST
        if form.validate_on_submit():
            ep_num = request.form['ep_num']
            date = request.form['date']
            num_items = request.form['num_items']
            theme = request.form['theme']
            is_presenter = request.form['is_presenter']
            episode = Episodes(ep_num, date, num_items, theme)
            db.session.add(episode)
            for key in request.form.keys():
                if key in getRogues(onlyNames=True):
                    if key == is_presenter:
                        correct = 'presenter'
                    else:
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
                               guests=getGuests(),
                               themes=getThemes()
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
