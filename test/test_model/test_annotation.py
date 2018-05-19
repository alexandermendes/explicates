# -*- coding: utf8 -*-

from flask import url_for
from nose.tools import *
from base import Test, db, with_context

from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class TestModelAnnotation(Test):

    def setUp(self):
        super(TestModelAnnotation, self).setUp()

    @with_context
    def test_iri(self):
        """Test Annotation IRI generated correctly."""
        collection_data = {
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ]
        }
        annotation_data = {
            'body': 'foo',
            'target': 'bar'
        }
        collection = Collection(data=collection_data)
        annotation = Annotation(collection=collection, data=annotation_data)
        db.session.add(collection)
        db.session.add(annotation)
        db.session.commit()
        expected = url_for('api.annotations',
                           collection_id=collection.id,
                           annotation_id=annotation.id,
                           _external=True)
        assert_equal(annotation.iri, expected)
