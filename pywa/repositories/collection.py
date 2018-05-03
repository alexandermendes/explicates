# -*- coding: utf8 -*-

from pywa.repositories import Repository


class CollectionRepository(Repository):

    def __init__(self, db):
        self.db = db
