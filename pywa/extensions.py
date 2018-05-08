# -*- coding: utf8 -*-

__all__ = ['db', 'flask_profiler']


# DB
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.slave_session = db.session

# Flask Profiler
import flask_profiler
