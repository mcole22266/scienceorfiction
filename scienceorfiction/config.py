from os import environ, urandom


class Config:
    '''
    Python representation of environment variables
    to be used within the app. If a new environment
    variable is added in an env file, it likely needs
    to also be added here to be used by Flask.
    '''

    # flask settings
    SECRET_KEY = urandom(32)
    FLASK_APP = environ["FLASK_APP"]
    FLASK_ENV = environ["FLASK_ENV"]
    FLASK_DEBUG = environ['FLASK_DEBUG']
    FLASK_HOST = environ['FLASK_HOST']
    FLASK_PORT = environ['FLASK_PORT']

    # db connection settings
    DB_WAIT_INITIAL = environ['DB_WAIT_INITIAL']
    DB_WAIT_MULTIPLIER = environ['DB_WAIT_MULTIPLIER']
    DB_WAIT_MAX = environ['DB_WAIT_MAX']

    # mysql settings
    MYSQL_DATABASE = environ['MYSQL_DATABASE']
    MYSQL_ROOT_PASSWORD = environ['MYSQL_ROOT_PASSWORD']

    # sqlalchemy settings
    SQLALCHEMY_DATABASE_URI = environ['SQLALCHEMY_DATABASE_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = environ['SQLALCHEMY_TRACK_MODIFICATIONS']

    # email settings
    GMAIL_USERNAME = environ['GMAIL_USERNAME']
    GMAIL_PASSWORD = environ['GMAIL_PASSWORD']

    # bokeh settings
    OUTPUT_FILEPATH = environ['OUTPUT_FILEPATH']
