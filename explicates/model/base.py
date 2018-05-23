# -*- coding: utf8 -*-
"""Base model."""

import os
import datetime
from flask import url_for, current_app
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Integer, Text, Unicode, Boolean
from sqlalchemy.schema import Column
from sqlalchemy.inspection import inspect as sa_inspect

from explicates.model.utils import make_timestamp, make_uuid


class BaseDomainObject(object):
    """Base domain object class."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    #: The object's primary key.
    key = Column(Integer, primary_key=True)

    #: The object's ID.
    id = Column(Unicode, unique=True, default=make_uuid)

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
        private = [
            'key',
            'id',
            '_data',
            'deleted',
            'collection_key',
            'data',
            'iri'
        ]
        out = {}

        # Add column values
        for col in self.__table__.c:
            obj = getattr(self, col.name)
            if not obj or col.name in private:
                continue
            elif isinstance(obj, datetime.datetime):
                obj = obj.isoformat()
            out[col.name] = obj

        # Add data
        if self._data:
            out.update(self._data)

        # Add hybrid properties
        for item in sa_inspect(self.__class__).all_orm_descriptors:
            if type(item) == hybrid_property and item.__name__ not in private:
                obj = getattr(self, item.__name__)
                out[item.__name__] = obj

        # Add generated
        out['generated'] = make_timestamp()

        # Add generator
        generator = current_app.config.get('GENERATOR')
        if generator:
            out['generator'] = generator

        # Add ID
        if self.iri:
            out['id'] = self.iri

        return out

    def update(self):
        """Set the modified time to now."""
        self.modified = make_timestamp()