# routes.py
# Created by: Michael Cole
# Updated by: Michael Cole
# -----------------------------
# Contains all routing information
# (and lots of logic for now).

from datetime import date, datetime
from threading import Thread

from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm

from .extensions import (addAdmin, addEpisode, addParticipant,
                         check_authentication, email_secret_code, encrypt,
                         generate_secret_code, getAdmin, getAllEpisodes,
                         getAllParticipants, getAllResults, getGuests,
                         getRogues, getThemes, getUserFriendlyEpisodeData,
                         getUserFriendlyEpisodeSums, getUserFriendlyGuests,
                         getUserFriendlyRogues, getYears)
from .forms import (AddEntryForm, AddParticipantForm, AdminAuthenticateForm,
                    AdminCreateForm, AdminLoginForm)
from .models import db


def addRoutes(app):
    '''
    This initializes a given app with all routes associated with the
    Science or Fiction app.

    Args:
        app (Flask App): An app to be initialized with routes
    Return:
        None
    '''
    @app.route('/', methods=['GET', 'POST'])
    def index():
        '''
        The index page for the Science or Fiction app. Works directly with
        other routes display different graphs based on a user-selected year.
        '''
        form = FlaskForm()

        # POST
        if form.validate_on_submit():
            # redirect to self with user-selected year to display the correct
            # Bokeh graph
            graphType = request.form['graphType']
            year = request.form['year']
            return redirect(url_for('index',
                                    graphType=graphType,
                                    graphYear=year))

        # GET
        # render template with default parameters where:
        #   year == current year | graph type == overall accuracy
        graphType = request.args.get('graphType', 'overallAccuracy')
        graphYear = request.args.get('graphYear', str(date.today().year))
        if graphYear == 'overall':
            graph = graphType
        else:
            graph = graphType + graphYear

        return render_template('index.html',
                               title='Science or Fiction',
                               form=form,
                               graph=graph,
                               graphType=graphType,
                               graphYear=graphYear,
                               years=getYears(desc=True),
                               themes=getThemes())

    @app.route('/overallAccuracy')
    def overallAccuracy():
        '''
        Exists to be redirected to the index page with a graph type of
        overallAccuracy.
        '''
        return redirect(url_for('index', graphType='overallAccuracy'))

    @app.route('/accuracyOverTime')
    def accuracyOverTime():
        '''
        Exists to be redirected to the index page with a graph type of
        accuracyOverTime.
        '''
        return redirect(url_for('index', graphType='accuracyOverTime'))

    @app.route('/sweeps')
    def sweeps():
        '''
        Exists to be redirected to the index page with a graph type of
        sweeps.
        '''
        return redirect(url_for('index', graphType='sweeps'))

    @app.route('/data')
    def data():
        '''
        Page that displays appropriate tables to the user.
        '''
        return render_template('data.html',
                               title='Science or Fiction',
                               userFriendlyRogues=getUserFriendlyRogues(db),
                               userFriendlyGuests=getUserFriendlyGuests(db),
                               ep_data=getUserFriendlyEpisodeData(db),
                               sum_data=getUserFriendlyEpisodeSums(db))

    @app.route('/about')
    def about():
        '''
        Contains information about the project and the developer behind it.
        '''
        return render_template('about.html')

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        '''
        Landing page for administrators of the project. Contains tables that
        are available to users as well as tables that mirror the database.
        Also provides administrators with the ability to add new entries to
        the db.
        - can only be access if logged in (redirects to /admin/login if not) -
        '''
        form = AddEntryForm()
        participantForm = AddParticipantForm()

        # find which form was submitted by checking for unique
        # form data as there are now multiple POSTS
        try:
            ep_num = request.form['ep_num']
            formType = 'add entry'
        except Exception:
            formType = 'add participant'

        # POST - add entry
        if formType == 'add entry':
            if form.validate_on_submit():
                # get form data
                ep_num = request.form['ep_num']
                ep_date = request.form['date']
                num_items = request.form['num_items']
                theme = request.form['theme']
                guests = []
                participant_results = []
                for key in request.form.keys():
                    if 'radio' in key:
                        if 'guest' not in key:
                            # remove 'radio-' from key by finding hyphen
                            participant = key[key.find('-')+1:]
                            result = request.form[key]
                        else:
                            # remove '-radio' from key by finding hyphen
                            guest = key[:key.find('-')]
                            participant = request.form[guest]
                            result = request.form[guest + '-radio']
                            guests.append(participant)
                        participant_results.append((participant, result))
                addEpisode(db, ep_num, ep_date, num_items, theme, guests,
                           participant_results, commit=True)
                return redirect(url_for('admin'))

        # POST - add participant
        if formType == 'add participant':
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
                               title='Science or Fiction - Admin',
                               form=form,
                               participantForm=participantForm,
                               rogues=getRogues(current_date=date.today()),
                               guests=getGuests(),
                               themes=getThemes(),
                               participants=getAllParticipants(),
                               episodes=getAllEpisodes(),
                               results=getAllResults(),
                               userFriendlyRogues=getUserFriendlyRogues(db),
                               userFriendlyGuests=getUserFriendlyGuests(db),
                               ep_data=getUserFriendlyEpisodeData(db),
                               sum_data=getUserFriendlyEpisodeSums(db),
                               admins=getAdmin(all=True),
                               today_date=date.today()
                               )

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        '''
        Contains form that allows an administrator to log into the app.
        Also contains a link to redirect an future-administrator to the
        creation form in order to become a new administrator.
        '''
        if current_user.is_authenticated:
            return redirect(url_for('admin'))
        form = AdminLoginForm()

        # POST
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']
            if check_authentication(username, password):
                admin = getAdmin(username)
                login_user(admin)
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('admin_login'))

        # GET
        return render_template('adminLogin.html',
                               title='Admin - Login',
                               form=form)

    @app.route('/admin/create', methods=['GET', 'POST'])
    def admin_create():
        '''
        Contains form that allows a future-administrator to create an
        admin account. Also contains a link to redirect a current-administrator
        to the admin login page.
        '''
        if current_user.is_authenticated:
            return redirect(url_for('admin'))
        form = AdminCreateForm()

        # POST
        if form.validate_on_submit():
            username = request.form['username']
            password = encrypt(request.form['password'])
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            return redirect(url_for('admin_authenticate',
                                    username=username,
                                    password=password,
                                    firstname=firstname,
                                    lastname=lastname))

        # GET
        return render_template('adminCreate.html',
                               title='Admin - Create',
                               form=form)

    @app.route('/admin/authenticate', methods=['GET', 'POST'])
    def admin_authenticate():
        '''
        Contains a form that allows a future-adminstrator to input a secret
        code that's given only by an admin with ultimate approval of admins.
        An Email containing a secret code is sent for approval and given to
        the potential admin. This is designed to prevent anyone who stumbles
        upon the admin page the ability to easily become an admin.
        '''
        if current_user.is_authenticated:
            return redirect(url_for('admin'))
        form = AdminAuthenticateForm()

        # POST
        if form.validate_on_submit():
            username = request.form['username']
            password = request.form['password']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            # get true secret code from hidden form value
            secret_code = request.form['secret_code']
            # get secret code that the user inputs
            secretcode_input = request.form['secretcode_input']
            if secretcode_input == secret_code:
                admin = addAdmin(db, username, password,
                                 firstname, lastname,
                                 encrypted=True, commit=True)
                login_user(admin)
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('admin_authenticate',
                                        username=username,
                                        password=password,
                                        firstname=firstname,
                                        lastname=lastname))

        # GET
        username = request.args.get('username')
        password = request.args.get('password')
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        secret_code = generate_secret_code()
        # Using a background process, send an email to the appropriate
        # address.
        thread = Thread(target=email_secret_code, args=[secret_code])
        thread.start()

        return render_template('adminAuthenticate.html',
                               title='Admin - Authenticate',
                               username=username,
                               password=password,
                               firstname=firstname,
                               lastname=lastname,
                               secret_code=secret_code,
                               form=form)

    @app.route('/logout')
    @login_required
    def logout():
        '''
        Only exists to log a currently logged-in user out of the application.
        After the user is logged out, they are redirected to /admin which will
        redirect them back to /admin/login as they are no longer a logged-in
        user.
        - can only be access if logged in (redirects to /admin/login if not) -
        '''
        logout_user()
        return redirect(url_for('admin'))

    @app.route('/refreshGraphs')
    @login_required
    def refreshGraphs():
        '''
        Exists in order to have all graphs in the bokeh folder updated with any
        new information that may exist.
        - can only be access if logged in (redirects to /admin/login if not) -
        '''
        from .extensions import init_graphs
        init_graphs(app)
        return redirect(url_for('admin'))
