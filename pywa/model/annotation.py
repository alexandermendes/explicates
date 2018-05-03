# -*- coding: utf8 -*-

from sqlalchemy.schema import Column
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB

from pywa.core import db
from pywa.model import make_timestamp, make_uuid
from pywa.model.collection import Collection


class Annotation(db.Model):
    """An annotation"""

    __tablename__ = 'annotation'

    #: The Annotation ID
    id = Column(Integer, primary_key=True)

    #: The IRI path segement appended to the Annotation IRI.
    slug = Column(Unicode(), unique=True, default=make_uuid())

    #: The relationship between the Annotation and its Body.
    body = Column(JSONB, nullable=False)

    #: The relationship between the Annotation and its Target.
    target = Column(JSONB, nullable=False)

    #: The time at which the Annotation was created.
    created = Column(Text, default=make_timestamp)

    #: The agent responsible for creating the Annotation.
    creator = Column(JSONB)

    #: The time at which the Annotation was modified, after creation.
    modified = Column(Text)

    #: The relationship between the Annotation and the Style.
    stylesheet = Column(JSONB)

    #: The related Collection.
    collection = relationship(Collection)
