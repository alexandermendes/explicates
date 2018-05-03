# -*- coding: utf8 -*-

from pywa.repositories import Repository


class AnnotationRepository(Repository):

    def __init__(self, db):
        self.db = db
