# -*- coding: utf-8 -*-

from explicates.model.collection import Collection
from . import BaseFactory, factory, repo


class CollectionFactory(BaseFactory):
    class Meta:
        model = Collection

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        collection = model_class(*args, **kwargs)
        repo.save(Collection, collection)
        return collection

    key = factory.Sequence(lambda n: n)
    id = factory.Sequence(lambda n: u'✓collection%d' % n)
    data = {
        'type': [
            'BasicContainer',
            'AnnotationCollection'
        ]
    }
