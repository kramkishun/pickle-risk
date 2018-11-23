from flask import Flask
from flask_pymongo import PyMongo

import pprint, json

from . import history
from . import multihistory

# To launch (in Windows Powershell/VSCode):
# > $env:FLASK_APP="pickle_risk"
# > $env:FLASK_ENV="development"
# > flask run

# To run all tests:
# > python -m unittest discover tests

# To run coverage on tests:
# > coverage run -m unittest discover tests
# > coverage report

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MONGO_URI='mongodb://localhost:27017/pickleRisk'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.register_blueprint(history.bp)
    app.register_blueprint(multihistory.bp)

    @app.route('/')
    def welcome():
        return 'Check out /history'

    return app


