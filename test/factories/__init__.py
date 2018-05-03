# -*- coding: utf8 -*-

from pywa.core import db

import factory

from pywa.repositories import AnnotationRepository
from pywa.repositories import CollectionRepository


annotation_repo = AnnotationRepository(db)
collection_repo = CollectionRepository(db)


def reset_all_pk_sequences():
    AnnotationFactory.reset_sequence()
    CollectionFactory.reset_sequence()


class BaseFactory(factory.Factory):
    @classmethod
    def _setup_next_sequence(cls):
        return 1

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        project = model_class(*args, **kwargs)
        db.session.remove()
        return project


# Import the factories
from annotation import AnnotationFactory
from collection import CollectionFactory
