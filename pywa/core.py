# -*- coding: utf8 -*-

import os
from flask import Flask

from pywa import default_settings
from pywa.extensions import *
from pywa.response import process_response


def create_app():
    """Create app."""
    app = Flask(__name__)
    app.process_response = process_response
    configure_app(app)
    setup_blueprints(app)
    return app


def configure_app(app):
    """Configure app."""
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


def setup_blueprints(app):
    """Setup blueprints."""
    from pywa.api.index import blueprint as index

    app.register_blueprint(index, url_prefix='/')
