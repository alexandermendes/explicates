# -*- coding: utf8 -*-
"""Extensions module."""

__all__ = ['db', 'cors', 'exporter']


# DB
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.slave_session = db.session

# CORS
from flask_cors import CORS
cors = CORS()

# Exporter
exporter = None
