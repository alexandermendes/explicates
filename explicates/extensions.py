# -*- coding: utf8 -*-
"""Extensions module."""

__all__ = ['db', 'flask_profiler', 'cors']


# DB
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.slave_session = db.session

# Flask Profiler
import flask_profiler

# CORS
from flask_cors import CORS
cors = CORS()
