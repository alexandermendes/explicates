# -*- coding: utf8 -*-
"""Collection model."""

from flask import url_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from explicates.core import db
from explicates.model.base import BaseDomainObject
from explicates.model.annotation import Annotation


Base = declarative_base(cls=BaseDomainObject)


class Collection(db.Model, Base):
    """An AnnotationCollection"""

    __tablename__ = 'collection'

    annotations = relationship(Annotation, backref='collection')

    @hybrid_property
    def total(self):
        return len(self.annotations)

    @hybrid_property
    def iri(self):
        if self.id:
            return url_for('api.collections', collection_id=self.id,
                           _external=True)
