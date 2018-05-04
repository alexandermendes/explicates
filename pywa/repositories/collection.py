# -*- coding: utf8 -*-

from pywa.repositories.base import BaseRepository
from pywa.model.collection import Collection


class CollectionRepository(BaseRepository):
    """Collection repository class."""

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
