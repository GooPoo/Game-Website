import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # FLASK_SECRET_KEY is stored in virtual environment.
    # ...\Wordle_Website\wordle-env\Scripts\activate.bat
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False