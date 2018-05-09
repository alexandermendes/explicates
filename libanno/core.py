# -*- coding: utf8 -*-

import os
from flask import Flask
from werkzeug.exceptions import HTTPException

from libanno import default_settings
from libanno.extensions import *
from libanno.response import ContextualResponse


def create_app():
    """Create app."""
    app = Flask(__name__)
    configure_app(app)
    setup_db(app)
    setup_repositories(app)
    setup_blueprints(app)
    setup_error_handler(app)
    setup_profiler(app)
    setup_cors(app)
    app.response_class = ContextualResponse
    import libanno.model.event_listeners
    return app


def configure_app(app):
    """Configure app."""
    app.config.from_object(default_settings)
    app.config.from_envvar('LIBANNO_SETTINGS', silent=True)
    if not os.environ.get('LIBANNO_SETTINGS'):
        here = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(here), 'settings.py')
        if os.path.exists(config_path):
            app.config.from_pyfile(config_path)
    else:
        config_path = os.path.abspath(os.environ.get('LIBANNO_SETTINGS'))

    # Override DB for testing
    if app.config.get('SQLALCHEMY_DATABASE_TEST_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.config['SQLALCHEMY_DATABASE_TEST_URI']

    # Enable missing Slave bind using Master node
    if app.config.get('SQLALCHEMY_BINDS') is None:
        print " * Database slave binds are misssing, adding Master as slave"
        app.config['SQLALCHEMY_BINDS'] = \
            dict(slave=app.config.get('SQLALCHEMY_DATABASE_URI'))

    app.url_map.strict_slashes = app.config.get('STRICT_SLASHES')


def setup_blueprints(app):
    """Setup blueprints."""
    from libanno.api.annotations import blueprint as annotations_bp
    app.register_blueprint(annotations_bp, url_prefix='/annotations')


def setup_repositories(app):
    """Setup repositories."""
    from libanno.repositories import AnnotationRepository
    from libanno.repositories import CollectionRepository

    from libanno.model.annotation import Annotation
    from libanno.model.collection import Collection

    global annotation_repo
    global collection_repo

    annotation_repo = AnnotationRepository(db, Annotation)
    collection_repo = CollectionRepository(db, Collection)


def setup_db(app):
    """Setup database."""
    def create_slave_session(db, bind):
        if (app.config.get('SQLALCHEMY_BINDS')['slave'] ==
                app.config.get('SQLALCHEMY_DATABASE_URI')):
            return db.session
        engine = db.get_engine(db.app, bind=bind)
        options = dict(bind=engine, scopefunc=_app_ctx_stack.__ident_func__)
        slave_session = db.create_scoped_session(options=options)
        return slave_session
    db.app = app
    db.init_app(app)
    db.slave_session = create_slave_session(db, bind='slave')
    if db.slave_session is not db.session:
        # flask-sqlalchemy does it already for default session db.session
        @app.teardown_appcontext
        def _shutdown_session(response_or_exc):  # pragma: no cover
            if app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']:
                if response_or_exc is None:
                    db.slave_session.commit()
            db.slave_session.remove()
            return response_or_exc


def setup_error_handler(app):
    """Setup generic error handler."""
    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        return dict(code=code, message=str(e)), code


def setup_profiler(app):
    if app.config.get('FLASK_PROFILER'):
        print " * Flask Profiler is enabled"
        flask_profiler.init_app(app)

def setup_cors(app):
    """Setup CORS."""
    cors.init_app(app, resources=app.config.get('CORS_RESOURCES'))
