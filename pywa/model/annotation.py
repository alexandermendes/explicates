# -*- coding: utf8 -*-

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from pywa.core import db
from pywa.model.base import BaseDomainObject
from pywa.model.collection import Collection


Base = declarative_base(cls=BaseDomainObject)


class Annotation(db.Model, Base):
    """An annotation"""

    __tablename__ = 'annotation'

    #: The related Collection ID.
    collection_key = Column(Integer, ForeignKey('collection.key'),
                            nullable=False)

    #: The related Collection.
    collection = relationship(Collection)

    def get_id_suffix(self):
        return u'{0}/{1}'.format(self.collection.slug, self.slug)
