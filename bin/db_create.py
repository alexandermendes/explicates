#!/usr/bin/env python

from alembic.config import Config

from pywa.core import db, create_app


app = create_app()


def db_create():
    """Create the db"""
    with app.app_context():
        db.create_all()
        alembic_cfg = Config("../alembic.ini")
        command.stamp(alembic_cfg, "head")


if __name__ == '__main__':
    db_create()
