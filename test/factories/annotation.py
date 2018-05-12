# -*- coding: utf8 -*-

from explicates.model.annotation import Annotation
from . import BaseFactory, factory, annotation_repo


class AnnotationFactory(BaseFactory):
    class Meta:
        model = Annotation

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        annotation = model_class(*args, **kwargs)
        annotation_repo.save(annotation)
        return annotation

    key = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: u'✓annotation%d' % n)
    collection = factory.SubFactory('factories.CollectionFactory')
    collection_key = factory.LazyAttribute(lambda anno: anno.collection.key)
    data = {
        'type': 'Annotation',
        'body': 'http://example.org/post1',
        'target': 'http://example.org'
    }
