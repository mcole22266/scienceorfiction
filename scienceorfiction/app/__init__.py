from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():

        @app.route('/')
        def index():
            return 'Hello World'

        return app
