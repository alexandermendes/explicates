# -*- coding: utf8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for

from pywa.core import collection_repo, annotation_repo


class TestApi(Test):

    def setUp(self):
        super(TestApi, self).setUp()

    @with_context
    def test_404_when_collection_does_not_exist(self):
        """Test 404 when Collection does not exist."""
        endpoint = u'/foo'
        res = self.app_get_json(endpoint)
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
        res = self.app_post_json(endpoint, data=data, headers=headers)
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
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json(endpoint)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collection', collection_slug=collection.slug),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'items': [anno.dictize() for anno in collection.annotations],
            'first': url_for('api.collection', collection_slug=collection.slug,
                             page=0)
        })

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
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json(endpoint)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collection', collection_slug=collection.slug),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'items': [anno.dictize() for anno in collection.annotations],
            'first': url_for('api.collection', collection_slug=collection.slug,
                             page=0),
            'last': url_for('api.collection', collection_slug=collection.slug,
                             page=last_page)
        })

    @with_context
    def test_get_annotation(self):
        """Test Annotation returned."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        endpoint = u'/{}/{}'.format(collection.slug, annotation.slug)
        res = self.app_get_json(endpoint)
        assert_equal(json.loads(res.data), annotation.dictize())

    @with_context
    def test_404_when_annotation_not_found(self):
        """Test 404 when Annotation does not exist."""
        collection = CollectionFactory()
        endpoint = u'/{}/{}'.format(collection.slug, 'foo')
        res = self.app_get_json(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_404_when_annotation_not_in_collection(self):
        """Test 404 when Annotation is not in the Collection."""
        collection1 = CollectionFactory()
        collection2 = CollectionFactory()
        annotation = AnnotationFactory(collection=collection1)
        endpoint = u'/{}/{}'.format(collection2.slug, annotation.slug)
        res = self.app_get_json(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_annotation_created(self):
        """Test Annotation created."""
        collection = CollectionFactory(slug='foo')
        endpoint = '/{}'.format(collection.slug)
        data = dict(body='bar', target='http://example.com')
        headers = {
            'Slug': 'baz'
        }
        res = self.app_post_json(endpoint, data=data, headers=headers)
        annotation = annotation_repo.get(1)
        assert_not_equal(annotation, None)
        annotation_dict = annotation.dictize()
        assert_equal(json.loads(res.data), annotation_dict)

        # Test Location header contains Annotation IRI
        assert_equal(res.headers.get('Location'), annotation_dict['id'])