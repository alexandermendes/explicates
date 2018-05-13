# -*- coding: utf8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for

from explicates.core import repo
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class TestAnnotationsAPI(Test):

    def setUp(self):
        super(TestAnnotationsAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    @with_context
    @freeze_time("1984-11-19")
    def test_get_annotation(self):
        """Test Annotation returned."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        _id = url_for('api.annotations',
                      collection_id=collection.id,
                      annotation_id=annotation.id)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': _id,
            'type': 'Annotation',
            'body': annotation.data['body'],
            'target': annotation.data['target'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR')
        }

        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)
        assert_equal(res.status_code, 200)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_annotation_headers(self):
        """Test Annotation headers."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        res = self.app_get_json_ld(endpoint)

        link = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'
        assert_equal(res.headers.get('Link'), link)
        ct = 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"'
        assert_equal(res.headers.get('Content-Type'), ct)
        allow = 'GET,PUT,DELETE,OPTIONS,HEAD'
        assert_equal(res.headers.get('Allow'), allow)
        assert_not_equal(res.headers.get('ETag'), None)

    @with_context
    def test_404_when_annotation_not_found(self):
        """Test 404 when Annotation does not exist."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}/{}/'.format(collection.id, 'foo')
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_404_when_annotation_not_in_collection(self):
        """Test 404 when Annotation is not in the Collection."""
        collection1 = CollectionFactory()
        collection2 = CollectionFactory()
        annotation = AnnotationFactory(collection=collection1)
        endpoint = u'/annotations/{}/{}/'.format(collection2.id,
                                                 annotation.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_410_when_annotation_used_to_exist(self):
        """Test 410 when Annotation used to exist."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection, deleted=True)
        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 410)

    @with_context
    @freeze_time("1984-11-19")
    def test_annotation_created(self):
        """Test Annotation created."""
        collection = CollectionFactory(id='foo')
        endpoint = '/annotations/{}/'.format(collection.id)
        data = dict(type='Annotation', body='bar', target='http://example.org')
        res = self.app_post_json_ld(endpoint, data=data)
        annotation = repo.get(Annotation, 1)
        assert_not_equal(annotation, None)

        _id = url_for('api.annotations',
                      collection_id=collection.id,
                      annotation_id=annotation.id)
        assert_dict_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': _id,
            'type': 'Annotation',
            'body': data['body'],
            'target': data['target'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR')
        })

        # Test 201
        assert_equal(res.status_code, 201)

        # Test Location header contains Annotation IRI
        assert_equal(res.headers.get('Location'), _id)

        # Test Link header
        link = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'
        assert_equal(res.headers.get('Link'), link)

    @with_context
    @freeze_time("1984-11-19")
    def test_annotation_created_with_slug(self):
        """Test Annotation created with slug."""
        collection = CollectionFactory(id='foo')
        endpoint = '/annotations/{}/'.format(collection.id)
        data = dict(type='Annotation', body='bar', target='http://example.org')
        slug = 'baz'
        headers = dict(slug=slug)
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)
        annotation = repo.get(Annotation, 1)
        assert_equal(annotation.id, slug)

    @with_context
    def test_annotation_deleted(self):
        """Test Annotation deleted."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        res = self.app_delete_json_ld(endpoint)

        assert_equal(annotation.deleted, True)
        assert_equal(res.status_code, 204)

    @with_context
    def test_deleted_annotations_no_longer_returned_in_collection(self):
        """Test deleted Annotations are not returned in the Collection."""
        pass

    @with_context
    @freeze_time("1984-11-19")
    def test_annotation_updated(self):
        """Test Annotation updated."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        data = annotation.dictize().copy()
        data['body'] = "My new body"
        assert_equal(annotation.modified, None)

        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        res = self.app_put_json_ld(endpoint, data=data)

        # Test object updated
        assert_equal(annotation.modified, '1984-11-19T00:00:00Z')

        # Test data
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.annotations',
                          collection_id=collection.id,
                          annotation_id=annotation.id),
            'type': 'Annotation',
            'body': data['body'],
            'target': data['target'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'modified': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR')
        })

        # Test 200
        assert_equal(res.status_code, 200)

        # Test Link header
        link = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'
        assert_equal(res.headers.get('Link'), link)
