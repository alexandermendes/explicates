# -*- coding: utf8 -*-

from libanno.repositories.base import BaseRepository
from libanno.model.collection import Collection


class CollectionRepository(BaseRepository):
    """Collection repository class."""

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
