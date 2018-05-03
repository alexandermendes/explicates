# -*- coding: utf8 -*-

from sqlalchemy.schema import Column
from sqlalchemy import Integer, Text
from sqlalchemy.dialects.postgresql import JSONB

from pywa.core import db
from pywa.model import make_timestamp


class Collection(db.Model):
    """An annotation collection"""

    __tablename__ = 'collection'

    #: The Collection ID
    id = Column(Integer, primary_key=True)

    #: A human readable label for the container.
    label = Column(Text)

    #: The time at which the Collection was created.
    created = Column(Text, default=make_timestamp)

    #: The agent responsible for creating the Collection.
    creator = Column(JSONB)

    #: The time at which the Collection was modified, after creation.
    modified = Column(Text)
