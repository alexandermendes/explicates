# -*- coding: utf8 -*-

from flask import current_app
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from pywa.core import db
from pywa.model import make_timestamp, make_uuid
from pywa.model.base import BaseDomainObject
from pywa.model.collection import Collection


class Annotation(db.Model, BaseDomainObject):
    """An annotation"""

    __tablename__ = 'annotation'

    #: The Annotation primary key.
    key = Column(Integer, primary_key=True)

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
    collection_key = Column(Integer, ForeignKey('collection.key'),
                            nullable=False)

    #: The related Collection.
    collection = relationship(Collection)

    def get_id_suffix(self):
        return u'{0}/{1}'.format(self.collection.slug, self.slug)

    def get_extra_info(self):
        return {
            'type': 'Annotation',
            'generated': make_timestamp(),
            'generator': current_app.config.get('GENERATOR')
        }
