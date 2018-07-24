# -*- coding: utf-8 -*-

from flask import url_for, current_app
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

    @with_context
    def test_default_language_set(self):
        """Test default language is set."""
        default_lang = current_app.config.get('FTS_DEFAULT')
        annotation_data = {
            'body': 'foo',
            'target': 'bar'
        }
        collection = Collection()
        annotation = Annotation(collection=collection, data=annotation_data)
        db.session.add(annotation)
        db.session.commit()
        assert_equal(annotation.language, default_lang)

    @with_context
    def test_alternative_language_set_from_single_body(self):
        """Test alternative language is set from a single body."""
        annotation_data = {
            'body': {
                'language': 'fr'
            },
            'target': 'bar'
        }
        collection = Collection()
        annotation = Annotation(collection=collection, data=annotation_data)
        db.session.add(annotation)
        db.session.commit()
        assert_equal(annotation.language, 'french')

    @with_context
    def test_alternative_language_set_from_multiple_bodies(self):
        """Test alternative language is set from multiple bodies."""
        annotation_data = {
            'body': [
                {
                    'language': ['de', 'fr']
                },
                {
                    'language': 'ru'
                }
            ],
            'target': 'bar'
        }
        collection = Collection()
        annotation = Annotation(collection=collection, data=annotation_data)
        db.session.add(annotation)
        db.session.commit()
        assert_equal(annotation.language, 'german')
