# -*- coding: utf8 -*-

import os
from flask import Flask

from pywa import default_settings
from pywa.extensions import *


def create_app():
    app = Flask(__name__)
    configure_app(app)
    return app


def configure_app(app):
    app.config.from_object(default_settings)
    app.config.from_envvar('PYWA_SETTINGS', silent=True)
    if not os.environ.get('PYWA_SETTINGS'):
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings_local.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)
    else:
        config_path = os.path.abspath(os.environ.get('PYWA_SETTINGS'))

    # Override DB for testing
    if app.config.get('SQLALCHEMY_DATABASE_TEST_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.config['SQLALCHEMY_DATABASE_TEST_URI']
