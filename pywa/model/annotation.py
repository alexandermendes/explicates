# -*- coding: utf8 -*-

from flask import current_app
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property

from pywa.core import db
from pywa.model import make_timestamp, make_uuid
from pywa.model.base import BaseDomainObject
from pywa.model.collection import Collection


class Annotation(db.Model, BaseDomainObject):
    """An annotation"""

    __tablename__ = 'annotation'

    #: The Annotation ID
    id = Column(Integer, primary_key=True)

    #: The IRI path segement appended to the Annotation IRI.
    slug = Column(Unicode(), unique=True, default=unicode(make_uuid()))

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

    #: The related Collection ID.
    collection_id = Column(Integer, ForeignKey('collection.id'),
                           nullable=False)

    #: The related Collection.
    collection = relationship(Collection)

    @hybrid_property
    def generator(self):
        return current_app.config.get('GENERATOR')

    @validates('body')
    def validate_body(self, key, body):
        self.validate_json(key, body, 'annotation_body.json')
        return body

    @validates('target')
    def validate_target(self, key, target):
        self.validate_json(key, target, 'annotation_target.json')
        return target
