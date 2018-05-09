# -*- coding: utf8 -*-

import os
import datetime
from flask import url_for, current_app
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, Text, Unicode, Boolean
from sqlalchemy.schema import Column
from sqlalchemy.inspection import inspect as sa_inspect

from libanno.model.utils import make_timestamp, make_uuid

try:
    from urllib import quote
except ImportError:  # py3
    from urllib.parse import quote


class BaseDomainObject(object):
    """Base domain object class."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #: The object's primary key.
    key = Column(Integer, primary_key=True)

    #: The IRI path segement appended to the object's IRI.
    slug = Column(Unicode, unique=True, default=unicode(make_uuid()))

    #: The time at which the object was created.
    created = Column(Text, default=make_timestamp)

    #: The time at which the object was modified, after creation.
    modified = Column(Text, onupdate=make_timestamp)

    #: The time at which the object was deleted.
    deleted = Column(Boolean, default=False)

    #: The modifiable JSON data.
    _data = Column(JSONB)

    @hybrid_property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    def dictize(self):
        """Return the domain object as a dictionary."""
        filtered = ['key', 'slug', '_data', 'deleted', 'collection_key']
        out = self._data or {}

        # Add column values
        for col in self.__table__.c:
            obj = getattr(self, col.name)
            if not obj or col.name in filtered:
                continue
            elif isinstance(obj, datetime.datetime):
                obj = obj.isoformat()
            out[col.name] = obj

        # Add hybrid properties
        for item in sa_inspect(self.__class__).all_orm_descriptors:
            if type(item) == hybrid_property and item.__name__ != 'data':
                obj = getattr(self, item.__name__)
                out[item.__name__] = obj

        # Add context
        out['@context'] = "http://www.w3.org/ns/anno.jsonld"

        # Add ID
        root_url = url_for('annotations.index', _external=True)
        safe_suffix = quote(self.get_id_suffix().encode('utf8'))
        out['id'] = root_url + safe_suffix

        # Add generated
        out['generated'] = make_timestamp()

        # Add generator
        generator = current_app.config.get('GENERATOR')
        if generator:
            out['generator'] = generator

        return out
