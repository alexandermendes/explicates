# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from pywa.core import db
from pywa.model.base import BaseDomainObject
from pywa.model.annotation import Annotation


Base = declarative_base(cls=BaseDomainObject)


class Collection(db.Model, Base):
    """An annotation collection"""

    __tablename__ = 'collection'

    annotations = relationship(Annotation, backref='collection')

    def get_id_suffix(self):
        return u'{}/'.format(self.slug)
