# -*- coding: utf8 -*-

from pywa.repositories import Repository
from pywa.model.annotation import Annotation


class AnnotationRepository(Repository):

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class
