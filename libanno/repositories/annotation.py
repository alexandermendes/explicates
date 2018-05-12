# -*- coding: utf8 -*-

from explicates.repositories.base import BaseRepository
from explicates.model.annotation import Annotation


class AnnotationRepository(BaseRepository):
    """Annotation repository class."""

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
