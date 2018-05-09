# -*- coding: utf8 -*-

from libanno.repositories.base import BaseRepository
from libanno.model.annotation import Annotation


class AnnotationRepository(BaseRepository):
    """Annotation repository class."""

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
