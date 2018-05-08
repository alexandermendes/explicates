# -*- coding: utf8 -*-

from sqlalchemy.schema import Column
from sqlalchemy import Integer, Text, Unicode
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property

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

    #: The time at which the Collection was created.
    created = Column(Text, default=make_timestamp)

    #: The time at which the Collection was modified, after creation.
    modified = Column(Text)

    #: The modifiable Collection data.
    _data = Column(JSONB)

    def get_id_suffix(self):
        return self.slug

    @hybrid_property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
