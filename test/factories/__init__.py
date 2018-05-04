# -*- coding: utf8 -*-

import factory

from pywa.core import db
from pywa.repositories import AnnotationRepository
from pywa.repositories import CollectionRepository
from pywa.model.annotation import Annotation
from pywa.model.collection import Collection


annotation_repo = AnnotationRepository(db, Annotation)
collection_repo = CollectionRepository(db, Collection)


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
