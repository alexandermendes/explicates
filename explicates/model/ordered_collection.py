# -*- coding: utf8 -*-
"""OrderedCollection model."""

from flask import url_for
from sqlalchemy.ext.declarative import declarative_base

from explicates.model.base import BaseDomainObject


Base = declarative_base(cls=BaseDomainObject)


class OrderedCollection(Base):
    """An OrderedCollection.

    See https://www.w3.org/ns/activitystreams#OrderedCollection

    This class is not persisted in the database but used for temporary
    collections of objects that may, or may not be Annotations, such as
    search results.
    """

    def __init__(self, tablename, items, endpoint):
        self.tablename = tablename
        self.items = items
        self.iri = url_for(endpoint, tablename=self.tablename, _external=True)
        self._data = {
            'type': 'OrderedCollection',
            'total': len(items)
        }
