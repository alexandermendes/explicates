# -*- coding: utf8 -*-

from flask import url_for
from nose.tools import *
from base import Test, db, with_context

from explicates.model.collection import Collection


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
        expected = url_for('api.collections', collection_id=collection.id)
        assert_equal(collection.iri, expected)
