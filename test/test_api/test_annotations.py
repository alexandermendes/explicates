# -*- coding: utf8 -*-

import os
import json
from nose.tools import *
from mock import patch, call
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for
from jsonschema.exceptions import ValidationError

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
    def test_collection_modified_when_annotation_created(self):
        """Test Collection modified time updated when Annotation created."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}/'.format(collection.id)
        data = dict(type='Annotation', body='bar', target='http://example.org')
        self.app_post_json_ld(endpoint, data=data)
        annotation = repo.get(Annotation, 1)
        assert_not_equal(annotation.created, None)
        assert_equal(collection.modified, annotation.created)

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
    @freeze_time("1984-11-19")
    def test_annotation_created_with_id_moved_to_via(self):
        """Test Annotation created with ID moved to via."""
        collection = CollectionFactory(id='foo')
        endpoint = '/annotations/{}/'.format(collection.id)
        old_id = 'bar'
        data = dict(type='Annotation', body='baz', target='http://example.org',
                    id=old_id)
        res = self.app_post_json_ld(endpoint, data=data)
        annotation = repo.get(Annotation, 1)
        assert_equal(annotation._data.get('via'), old_id)
        assert_not_equal(annotation.id, old_id)
        assert_not_equal(annotation.dictize()['id'], old_id)

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
    @freeze_time("1984-11-19")
    def test_collection_modified_when_annotation_deleted(self):
        """Test Collection modified time updated when Annotation deleted."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        self.app_delete_json_ld(endpoint)
        assert_equal(annotation.deleted, True)
        assert_not_equal(annotation.modified, None)
        assert_equal(collection.modified, annotation.modified)

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

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_modified_when_annotation_updated(self):
        """Test Collection modified time updated when Annotation updated."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        data = annotation.dictize().copy()
        data['body'] = "My new body"
        endpoint = u'/annotations/{}/{}/'.format(collection.id,
                                                 annotation.id)
        self.app_put_json_ld(endpoint, data=data)
        assert_not_equal(annotation.modified, None)
        assert_equal(collection.modified, annotation.modified)

    @with_context
    @patch('explicates.api.base.validate_json')
    def test_annotation_validated_before_create(self, mock_validate):
        """Test Annotation validated before creation."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}/'.format(collection.id)
        bad_data = {'foo': 'bar'}
        mock_validate.side_effect = ValidationError('Bad Data')
        res = self.app_post_json_ld(endpoint, data=bad_data)
        assert_equal(res.status_code, 400)
        schema_path = os.path.join(current_app.root_path, 'schemas',
                                   'annotation.json')
        schema = json.load(open(schema_path))
        mock_validate.assert_called_once_with(bad_data, schema)
        annotations = repo.filter_by(Annotation)
        assert_equal(len(annotations), 0)

    @with_context
    @patch('explicates.api.base.validate_json')
    def test_annotation_validated_before_update(self, mock_validate):
        """Test Annotation validated before update."""
        annotation = AnnotationFactory()
        endpoint = u'/annotations/{}/{}/'.format(annotation.collection.id,
                                                 annotation.id)
        bad_data = {'foo': 'bar'}
        mock_validate.side_effect = ValidationError('Bad Data')
        res = self.app_put_json_ld(endpoint, data=bad_data)
        assert_equal(res.status_code, 400)
        schema_path = os.path.join(current_app.root_path, 'schemas',
                                   'annotation.json')
        schema = json.load(open(schema_path))
        mock_validate.assert_called_once_with(bad_data, schema)
        assert_not_equal(annotation._data, bad_data)
