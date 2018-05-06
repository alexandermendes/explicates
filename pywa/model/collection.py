# -*- coding: utf8 -*-

from sqlalchemy.schema import Column
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB

from pywa.core import db
from pywa.model import make_timestamp, make_uuid
from pywa.model.base import BaseDomainObject


class Collection(db.Model, BaseDomainObject):
    """An annotation collection"""

    __tablename__ = 'collection'

    #: The Collection primary key
    key = Column(Integer, primary_key=True)

    #: The IRI path segement appended to the Collection IRI.
    slug = Column(Unicode(), unique=True, default=unicode(make_uuid()))

    #: A human readable label for the Collection.
    label = Column(Text)

    #: The time at which the Collection was created.
    created = Column(Text, default=make_timestamp)

    #: The agent responsible for creating the Collection.
    creator = Column(JSONB)

    #: The time at which the Collection was modified, after creation.
    modified = Column(Text)
