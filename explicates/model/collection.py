# -*- coding: utf8 -*-
"""Collection model."""

from flask import url_for
from sqlalchemy import func, and_
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

    annotations = relationship(Annotation, backref='collection',
                               lazy='dynamic')

    @hybrid_property
    def total(self):
        count_q = func.count(Annotation.id) \
                      .filter(Annotation.deleted == False) \
                      .filter(Annotation.collection_key == self.key)
        return db.session.execute(db.session.query(count_q)).scalar()

    @total.expression
    def total(cls):
        return (select([func.count(Annotation.id)]).
                and_(
                    where(Annotation.collection_key == cls.key),
                    where(Annotation.deleted == False)).
                label("total"))

    @hybrid_property
    def iri(self):
        if self.id:
            return url_for('api.collections', collection_id=self.id,
                           _external=True)
