# -*- coding: utf-8 -*-

from flask import url_for
from nose.tools import *
from base import Test, db, with_context

from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class TestModelCollection(Test):

    def setUp(self):
        super(TestModelCollection, self).setUp()

    @with_context
    def test_iri(self):
        """Test Collection IRI generated correctly."""
        collection_data = {
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ]
        }
        collection = Collection(data=collection_data)
        db.session.add(collection)
        db.session.commit()
        expected = url_for('api.collections', collection_id=collection.id,
                           _external=True)
        assert_equal(collection.iri, expected)

    @with_context
    def test_total_returns_n_annotations(self):
        """Test Collection total contains number of Annotations."""
        collection_data = {
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ]
        }
        anno_data = {
            'body': 'foo',
            'target': 'bar'
        }
        collection = Collection(data=collection_data)
        annotation = Annotation(collection=collection, data=anno_data)
        db.session.add(collection)
        db.session.add(annotation)
        db.session.commit()
        assert_equal(collection.total, 1)
