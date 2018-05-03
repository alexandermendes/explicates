# -*- coding: utf8 -*-

from sqlalchemy.schema import Column
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB

from pywa.core import db
from pywa.model import make_timestamp, make_uuid
from pywa.model.collection import Collection


class Collection(db.Model):
    """An annotation collection"""

    __tablename__ = 'collection'

    #: The Collection ID
    id = Column(Integer, primary_key=True)

    #: The IRI path segement appended to the Collection IRI.
    slug = Column(Unicode(), unique=True, default=make_uuid())

    #: A human readable label for the Collection.
    label = Column(Text)

    #: The time at which the Collection was created.
    created = Column(Text, default=make_timestamp)

    #: The agent responsible for creating the Collection.
    creator = Column(JSONB)

    #: The time at which the Collection was modified, after creation.
    modified = Column(Text)

    #: The related Collection.
    collection = relationship(Collection)
