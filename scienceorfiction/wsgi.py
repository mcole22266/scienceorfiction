# wsgi.py
# Created by: Michael Cole
# Updated by: Michael Cole
# -----------------------------
# Runs a Flask server
# Standard App Factory setup

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
