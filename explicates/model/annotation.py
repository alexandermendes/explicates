# -*- coding: utf8 -*-
"""Annotation model module."""

from flask import url_for
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base

from explicates.core import db
from explicates.model.base import BaseDomainObject


Base = declarative_base(cls=BaseDomainObject)


class Annotation(db.Model, Base):
    """An Annotation"""

    __tablename__ = 'annotation'

    #: The related Collection ID.
    collection_key = Column(Integer, ForeignKey('collection.key'),
                            nullable=False)

    @hybrid_property
    def iri(self):
        if self.id:
            return url_for('api.annotations', collection_id=self.collection.id,
                           annotation_id=self.id, _external=True)
