# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base

from pywa.core import db
from pywa.model.base import BaseDomainObject


Base = declarative_base(cls=BaseDomainObject)


class Collection(db.Model, Base):
    """An annotation collection"""

    __tablename__ = 'collection'

    def get_id_suffix(self):
        return self.slug
