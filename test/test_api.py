# -*- coding: utf8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for
from rdflib import *

from pywa.core import collection_repo, annotation_repo

try:
    from urllib import urlencode
except ImportError:  # py3
    from urllib.parse import urlencode


class TestApi(Test):

    def setUp(self):
        super(TestApi, self).setUp()

    def convert_json(self, json, out_format):
        """Convert JSON to an alternative representation."""
        g = ConjunctiveGraph()
        g.parse(data=json, format="json-ld")
        return g.serialize(format=out_format)

    @with_context
    def test_404_when_collection_does_not_exist(self):
        """Test 404 when Collection does not exist."""
        endpoint = u'/foo'
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_created(self):
        """Test Collection created."""
        endpoint = '/'
        data = dict(type='AnnotationCollection', label='foo')
        headers = {
            'Slug': 'bar'
        }
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)
        collection = collection_repo.get(1)
        assert_not_equal(collection, None)
        collection_dict = collection.dictize()
        assert_equal(json.loads(res.data), collection_dict)

        # Test response contains the new collection
        _id = url_for('api.collection', collection_slug=collection.slug)
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

        # Test Location header contains Collection IRI
        assert_equal(res.headers.get('Location'), _id)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_collection_with_first_page(self):
        """Test Collection returned with first page."""
        collection = CollectionFactory()
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        annotations = AnnotationFactory.create_batch(per_page,
                                                     collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collection', collection_slug=collection.slug),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': url_for('api.collection', collection_slug=collection.slug,
                             page=0)
        }

        # Test JSON response
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

        # Test Turtle response
        res = self.app_get_turtle(endpoint)
        expected_turtle = self.convert_json(json.dumps(expected), 'turtle')
        assert_equal(res.data, expected_turtle)

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
            'id': url_for('api.collection', collection_slug=collection.slug),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': url_for('api.collection', collection_slug=collection.slug,
                             page=0),
            'last': url_for('api.collection', collection_slug=collection.slug,
                             page=last_page)
        }

        # Test JSON response
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

        # Test Turtle response
        res = self.app_get_turtle(endpoint)
        expected_turtle = self.convert_json(json.dumps(expected), 'turtle')
        assert_equal(res.data, expected_turtle)

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
            'id': url_for('api.collection', collection_slug=collection.slug,
                          **kwargs),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': url_for('api.collection', collection_slug=collection.slug,
                             page=0, **kwargs),
            'last': url_for('api.collection', collection_slug=collection.slug,
                             page=last_page, **kwargs)
        }

        # Test JSON response
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json_ld(endpoint + "?" + query_str)
        assert_equal(json.loads(res.data), expected)

        # Test Turtle response
        res = self.app_get_turtle(endpoint + "?" + query_str)
        expected_turtle = self.convert_json(json.dumps(expected), 'turtle')
        assert_equal(res.data, expected_turtle)

    @with_context
    def test_last_collection_cannot_be_deleted(self):
        """Test the last Collection cannot be deleted."""
        collection = CollectionFactory()
        endpoint = u'/{}'.format(collection.slug)

        res = self.app_delete_json_ld(endpoint)
        assert_equal(res.status_code, 400)

        collection_after = collection_repo.get(1)
        assert_equal(collection, collection_after)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_annotation(self):
        """Test Annotation returned."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': annotation.data['id'],
            'type': 'Annotation',
            'body': annotation.data['body'],
            'target': annotation.data['target'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR')
        }

        # Test JSON response
        endpoint = u'/{}/{}'.format(collection.slug, annotation.slug)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

        # Test Turtle response
        res = self.app_get_turtle(endpoint)
        expected_turtle = self.convert_json(json.dumps(expected), 'turtle')
        assert_equal(res.data, expected_turtle)

    @with_context
    def test_404_when_annotation_not_found(self):
        """Test 404 when Annotation does not exist."""
        collection = CollectionFactory()
        endpoint = u'/{}/{}'.format(collection.slug, 'foo')
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_404_when_annotation_not_in_collection(self):
        """Test 404 when Annotation is not in the Collection."""
        collection1 = CollectionFactory()
        collection2 = CollectionFactory()
        annotation = AnnotationFactory(collection=collection1)
        endpoint = u'/{}/{}'.format(collection2.slug, annotation.slug)
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    @freeze_time("1984-11-19")
    def test_annotation_created(self):
        """Test Annotation created."""
        collection = CollectionFactory(slug='foo')
        endpoint = '/{}'.format(collection.slug)
        data = dict(type='Annotation', body='bar', target='http://example.org')
        headers = {
            'Slug': 'baz'
        }
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)
        annotation = annotation_repo.get(1)
        assert_not_equal(annotation, None)
        annotation_dict = annotation.dictize()
        assert_equal(json.loads(res.data), annotation_dict)

        _id = url_for('api.annotation', collection_slug=collection.slug,
                      annotation_slug=annotation.slug)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': _id,
            'type': 'Annotation',
            'body': data['body'],
            'target': data['target'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR')
        })

        # Test Location header contains Annotation IRI
        assert_equal(res.headers.get('Location'), _id)