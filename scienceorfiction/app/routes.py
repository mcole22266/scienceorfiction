# Contains all routing information (and lots of logic for now)

from datetime import date
from threading import Thread

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from .extensions import (addAdmins, addEpisode, check_authentication,
                         email_secret_code, encrypt, generate_secret_code,
                         getAdmins, getGuests, getRogues, getThemes)
from .forms import (AddEntryForm, AdminAuthenticateForm, AdminCreateForm,
                    AdminLoginForm)
from .graphs import (graphRogueAccuracies, graphRogueOverallAccuracies,
                     graphSweeps)
from .models import db
from .stats import getRogueAttendance, getRogueOverallAccuracy, getSweeps

secret_code = generate_secret_code()


def addRoutes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index(filename='rogueOverallAccuracies.html'):
        graphs = ['Rogue Accuracies',
                  'Rogue Accuracies for Star Wars',
                  'Rogue Accuracies Over Time',
                  'Rogue Accuracies Over Time for Star Wars',
                  'Sweeps Over Time']
        form = FlaskForm()

        # POST
        if form.validate_on_submit():
            graph_choice = request.form['graph_choice']
            if graph_choice == 'Rogue Accuracies Over Time':
                filename = 'rogueAccuracies.html'
                graphRogueAccuracies(filename)
            elif graph_choice == 'Rogue Accuracies Over Time for Star Wars':
                filename = 'rogueAccuraciesStarWars.html'
                graphRogueAccuracies(filename, theme='Star Wars')
            elif graph_choice == 'Sweeps Over Time':
                filename = 'sweeps.html'
                graphSweeps(filename)
            elif graph_choice == 'Rogue Accuracies':
                filename = 'rogueOverallAccuracies.html'
                graphRogueOverallAccuracies(filename)
            elif graph_choice == 'Rogue Accuracies for Star Wars':
                filename = 'rogueOverallAccuraciesStarWars.html'
                graphRogueOverallAccuracies(filename, theme='Star Wars')
            return redirect(url_for('index', filename=filename))

        # GET
        graphRogueOverallAccuracies(filename)
        if request.args.get('filename'):
            filename = request.args.get('filename')
        return render_template('index.html',
                               title='Hello World',
                               form=form,
                               graphs=graphs,
                               filename=filename)

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

        # POST
        if form.validate_on_submit():
            ep_num = request.form['ep_num']
            date = request.form['date']
            num_items = request.form['num_items']
            theme = request.form['theme']
            is_presenter = request.form['is_presenter']
            participant_results = []
            for key in request.form.keys():
                if key in getRogues(onlyNames=True):
                    if key == is_presenter:
                        correct = 'presenter'
                    else:
                        correct = request.form[key]
                    participant_results.append((key, correct))
            addEpisode(db, ep_num, date, num_items, theme,
                       participant_results, commit=True)
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
