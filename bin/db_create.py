#!/usr/bin/env python

import os
from alembic.config import Config
from alembic import command

from explicates.core import db, create_app
from explicates.model.collection import Collection


app = create_app()


def db_create():
    """Create the db"""
    with app.app_context():
        db.create_all()
        here = os.path.dirname(os.path.abspath(__file__))
        cfg_path = os.path.join(os.path.dirname(here), "alembic.ini")
        alembic_cfg = Config(cfg_path)
        command.stamp(alembic_cfg, "head")

        # Annotation servers must provide at least one container
        collection = Collection(id="default", data={
            'type': ['AnnotationCollection', 'BasicContainer'],
            'label': 'Default Container'
        })
        db.session.add(collection)
        db.session.commit()


if __name__ == '__main__':
    db_create()
