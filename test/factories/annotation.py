# -*- coding: utf8 -*-

from pywa.model.annotation import Annotation
from . import BaseFactory, factory, annotation_repo


class AnnotationFactory(BaseFactory):
    class Meta:
        model = Annotation

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        annotation = model_class(*args, **kwargs)
        annotation_repo.save(task)
        return annotation

    id = factory.Sequence(lambda n: n)
    collection = factory.SubFactory('factories.CollectionFactory')
    collection_id = factory.LazyAttribute(lambda anno: anno.collection.id)
