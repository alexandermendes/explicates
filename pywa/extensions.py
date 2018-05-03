# -*- coding: utf8 -*-

from flask_sqlalchemy import SQLAlchemy


__all__ = ['db']


# DB
db = SQLAlchemy()
db.slave_session = db.session
