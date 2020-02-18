# Contains all routing information (and lots of logic for now)

from datetime import date, datetime
from threading import Thread

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from .extensions import (addAdmins, addEpisode, addParticipant,
                         check_authentication, email_secret_code, encrypt,
                         generate_secret_code, getAdmins, getAllEpisodes,
                         getAllParticipants, getAllResults, getGuests,
                         getRogues, getThemes, getUserFriendlyRogues,
                         getYears)
from .forms import (AddEntryForm, AddParticipantForm, AdminAuthenticateForm,
                    AdminCreateForm, AdminLoginForm)
from .graphs import getGraph
from .models import db
from .stats import getRogueAttendance, getRogueOverallAccuracy, getSweeps

secret_code = generate_secret_code()


def addRoutes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = FlaskForm()

        # POST
        if form.validate_on_submit():
            graphType = request.form['graphType']
            year = request.form['year']
            try:
                theme = request.form['theme']
            except Exception:
                theme = ''
            return redirect(url_for('index',
                                    graphType=graphType,
                                    graphYear=year,
                                    graphTheme=theme))

        # GET
        graphType = request.args.get('graphType', 'overallAccuracy')
        graphYear = request.args.get('graphYear', str(date.today().year))
        graphTheme = request.args.get('graphTheme', '')

        graph = getGraph(graphType, graphYear, graphTheme)
        return render_template('index.html',
                               title='Hello World',
                               form=form,
                               graph=graph,
                               graphType=graphType,
                               graphYear=graphYear,
                               graphTheme=graphTheme,
                               years=getYears(),
                               themes=getThemes())

    @app.route('/overallAccuracy')
    def overallAccuracy():
        return redirect(url_for('index', graphType='overallAccuracy'))

    @app.route('/accuracyOverTime')
    def accuracyOverTime():
        return redirect(url_for('index', graphType='accuracyOverTime'))

    @app.route('/sweeps')
    def sweeps():
        return redirect(url_for('index', graphType='sweeps'))

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/stats')
    def stats():
        rogueAccuracies = []
        rogueAccuracies2019 = []
        rogueAccuraciesStarWars = []
        rogueAttendances = []
        startdate = date(2019, 1, 1)
        enddate = date(2019, 12, 31)
        rogues = getRogues(onlyNames=True)
        for rogue in rogues:
            accuracy = getRogueOverallAccuracy(rogue)
            rogueAccuracies.append((rogue, accuracy))
        for rogue in rogues:
            accuracy = getRogueOverallAccuracy(rogue,
                                               daterange=(startdate, enddate))
            rogueAccuracies2019.append((rogue, accuracy))
        for rogue in rogues:
            theme = 'Star Wars'
            accuracy = getRogueOverallAccuracy(rogue, theme=theme)
            rogueAccuraciesStarWars.append((rogue, accuracy))
        for rogue in rogues:
            attendance = getRogueAttendance(rogue)
            rogueAttendances.append((rogue, attendance))
        presenterSweeps = getSweeps(presenter=True)
        numPresenterSweeps = str(len(presenterSweeps))
        participantSweeps = getSweeps(participant=True)
        numParticipantSweeps = str(len(participantSweeps))
        presenterSweeps19 = getSweeps(presenter=True,
                                      daterange=(startdate, enddate))
        numPresenterSweeps19 = str(len(presenterSweeps19))
        participantSweeps19 = getSweeps(participant=True,
                                        daterange=(startdate, enddate))
        numParticipantSweeps19 = str(len(participantSweeps19))

        return render_template('stats.html',
                               title='Testing - Statistics',
                               rogueAccuracies=rogueAccuracies,
                               rogueAccuracies2019=rogueAccuracies2019,
                               rogueAccuraciesStarWars=rogueAccuraciesStarWars,
                               rogueAttendances=rogueAttendances,
                               presenterSweeps=presenterSweeps,
                               numPresenterSweeps=numPresenterSweeps,
                               participantSweeps=participantSweeps,
                               numParticipantSweeps=numParticipantSweeps,
                               presenterSweeps2019=presenterSweeps19,
                               numPresenterSweeps2019=numPresenterSweeps19,
                               participantSweeps2019=participantSweeps19,
                               numParticipantSweeps2019=numParticipantSweeps19
                               )

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        form = AddEntryForm()
        participantForm = AddParticipantForm()

        # POST
        if form.validate_on_submit():
            ep_num = request.form['ep_num']
            ep_date = request.form['date']
            num_items = request.form['num_items']
            theme = request.form['theme']
            guests = []
            participant_results = []
            for key in request.form.keys():
                app.logger.info(key)
                if 'radio' in key:
                    if 'guest' not in key:
                        # remove 'radio-' from key by finding hyphen
                        participant = key[key.find('-')+1:]
                        result = request.form[key]
                    else:
                        # remove '-radio' from key by finding hyphen
                        guest = key[:key.find('-')]
                        app.logger.info('guest: ' + guest)
                        participant = request.form[guest]
                        app.logger.info('participant: ' + participant)
                        result = request.form[guest + '-radio']
                        app.logger.info('result: ' + result)
                        guests.append(participant)
                    participant_results.append((participant, result))
            addEpisode(db, ep_num, ep_date, num_items, theme, guests,
                       participant_results, commit=True)
            return redirect(url_for('admin'))

        if participantForm.validate_on_submit():
            name = request.form['name']
            try:
                is_rogue = request.form['is_rogue']
            except Exception:
                is_rogue = False
            if is_rogue:
                start_date = request.form['rogue_start_date']
                if start_date != '':
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                else:
                    start_date = None
                end_date = request.form['rogue_end_date']
                if end_date != '':
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                else:
                    end_date = None
                addParticipant(db, name, is_rogue=True,
                               rogue_start_date=start_date,
                               rogue_end_date=end_date,
                               commit=True)
            else:
                addParticipant(db, name, commit=True)

            return redirect(url_for('admin'))

        # GET
        return render_template('admin.html',
                               title='Admin - Add Entry',
                               form=form,
                               participantForm=participantForm,
                               rogues=getRogues(current_date=date.today()),
                               guests=getGuests(),
                               themes=getThemes(),
                               participants=getAllParticipants(),
                               episodes=getAllEpisodes(),
                               results=getAllResults(),
                               userFriendlyRogues=getUserFriendlyRogues(db),
                               today_date=date.today()
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
                admin = getAdmins(username)
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
                admin = addAdmins(db, username, password,
                                  encrypted=True, commit=True)
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
