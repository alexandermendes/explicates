# -*- coding: utf8 -*-

from flask import current_app
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

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

    #: The time at which the Annotation was created.
    created = Column(Text, default=make_timestamp)

    #: The time at which the Annotation was modified, after creation.
    modified = Column(Text)

    #: The modifiable Annotation data
    _data = Column(JSONB)

    #: The related Collection ID.
    collection_key = Column(Integer, ForeignKey('collection.key'),
                            nullable=False)

    #: The related Collection.
    collection = relationship(Collection)

    def get_id_suffix(self):
        return u'{0}/{1}'.format(self.collection.slug, self.slug)

    def get_extra_info(self):
        info = {
            'type': 'Annotation',
            'generated': make_timestamp()
        }

        generator = current_app.config.get('GENERATOR')
        if generator:
            info['generator'] = generator

        return info

    @hybrid_property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
