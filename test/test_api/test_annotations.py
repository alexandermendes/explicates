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

try:
    from urllib import urlencode
except ImportError:  # py3
    from urllib.parse import urlencode


class TestApi(Test):

    def setUp(self):
        super(TestApi, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    def convert_json(self, json, out_format):
        """Convert JSON to an alternative representation."""
        g = ConjunctiveGraph()
        g.parse(data=json, format="json-ld")
        return g.serialize(format=out_format)

    @with_context
    def test_404_when_collection_does_not_exist(self):
        """Test 404 when Collection does not exist."""
        endpoint = '/annotations/invalid-collection/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_410_when_collection_used_to_exist(self):
        """Test 410 when Collection used to exist."""
        collection = CollectionFactory(deleted=True)
        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 410)

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_created(self):
        """Test Collection created."""
        endpoint = '/annotations/'
        data = dict(type='AnnotationCollection', label='foo')
        headers = {
            'Slug': 'bar'
        }
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)
        collection = repo.get(Collection, 1)
        assert_not_equal(collection, None)

        # Test response contains the new collection
        _id = url_for('api.collections', collection_id=collection.id)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': _id,
            'type': data['type'],
            'label': data['label'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 0
        })

        # Test 201
        assert_equal(res.status_code, 201)

        # Test Location header contains Collection IRI
        assert_equal(res.headers.get('Location'), _id)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_collection_with_first_page(self):
        """Test Collection returned with first page."""
        collection = CollectionFactory()
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': url_for('api.collections',
                             collection_id=collection.id,
                             page=0)
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_collection_with_last_page(self):
        """Test Collection returned with last page."""
        collection = CollectionFactory()
        n_pages = 3
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = n_pages - 1
        annotations = AnnotationFactory.create_batch(per_page * n_pages,
                                                     collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections',
                          collection_id=collection.id),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': url_for('api.collections',
                             collection_id=collection.id,
                             page=0),
            'last': url_for('api.collections',
                            collection_id=collection.id,
                            page=last_page)
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_collection_with_query_string(self):
        """Test Collection returned with query string."""
        collection = CollectionFactory()
        n_pages = 3
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = n_pages - 1
        annotations = AnnotationFactory.create_batch(per_page * n_pages,
                                                     collection=collection)

        kwargs = {
            'iris': 1
        }
        query_str = urlencode(kwargs)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections',
                          collection_id=collection.id,
                          **kwargs),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': url_for('api.collections',
                             collection_id=collection.id,
                             page=0, **kwargs),
            'last': url_for('api.collections',
                            collection_id=collection.id,
                            page=last_page, **kwargs)
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint + "?" + query_str)
        assert_equal(json.loads(res.data), expected)

    @with_context
    def test_last_collection_cannot_be_deleted(self):
        """Test the last Collection cannot be deleted."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_delete_json_ld(endpoint)
        assert_equal(res.status_code, 400)

        assert_equal(collection.deleted, False)

    @with_context
    def test_non_empty_collection_cannot_be_deleted(self):
        """Test non-empty Collection cannot be deleted."""
        collection = CollectionFactory()

        annotation = AnnotationFactory(collection=collection)
        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_delete_json_ld(endpoint)
        assert_equal(res.status_code, 400)

        assert_equal(collection.deleted, False)

    @with_context
    def test_collection_deleted(self):
        """Test Collection deleted."""
        collections = CollectionFactory.create_batch(2)
        collection = collections[0]

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_delete_json_ld(endpoint)
        assert_equal(res.status_code, 204)

        assert_equal(collection.deleted, True)

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_updated(self):
        """Test Collection updated."""
        collection = CollectionFactory()
        data = collection.dictize().copy()
        data['label'] = "My new label"
        assert_equal(collection.modified, None)

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_put_json_ld(endpoint, data=data)

        # Test object updated
        assert_equal(collection.modified, '1984-11-19T00:00:00Z')

        # Test data
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections',
                          collection_id=collection.id),
            'type': data['type'],
            'label': data['label'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'modified': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 0
        })

        # Test 200
        assert_equal(res.status_code, 200)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_collection_headers(self):
        """Test Collection headers."""
        collection_data = {
            'type': [
                'BasicContainer',
                'AnnotationCollection'
            ]
        }
        collection = CollectionFactory(data=collection_data)
        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)

        assert_equal(res.headers.getlist('Link'), [
            '<http://www.w3.org/ns/oa#AnnotationCollection>; rel="type"',
            '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"',
            '<http://www.w3.org/TR/annotation-protocol/>; ' +
            'rel="http://www.w3.org/ns/ldp#constrainedBy"'
        ])
        ct = 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"'
        assert_equal(res.headers.get('Content-Type'), ct)
        allow = 'GET,POST,PUT,DELETE,OPTIONS,HEAD'
        assert_equal(res.headers.get('Allow'), allow)
        assert_not_equal(res.headers.get('ETag'), None)

    def test_different_container_types(self):
        """Such as Direct and Indirect containers."""
        pass

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
        headers = {
            'Slug': 'baz'
        }
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)

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
