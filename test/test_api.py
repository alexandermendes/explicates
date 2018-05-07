# -*- coding: utf8 -*-

import json
from nose.tools import assert_equal
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory

from pywa.core import collection_repo, annotation_repo


class TestApi(Test):

    def setUp(self):
        super(TestApi, self).setUp()

    @with_context
    def test_get_collection(self):
        """Test Collection returned."""
        collection = CollectionFactory()
        endpoint = u'/{}'.format(collection.slug)
        res = self.app_get_json(endpoint)
        assert_equal(json.loads(res.data), collection.dictize())

    @with_context
    def test_404_when_collection_does_not_exist(self):
        """Test 404 when Collection does not exist."""
        endpoint = u'/foo'
        res = self.app_get_json(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_collection_created(self):
        """Test Collection created."""
        endpoint = '/'
        data = dict(label='foo')
        headers = {
            'Slug': 'bar'
        }
        res = self.app_post_json(endpoint, data=data, headers=headers)
        collection = collection_repo.get(1)
        collection_dict = collection.dictize()
        assert_equal(json.loads(res.data), collection_dict)

        # Test Location header contains Collection IRI
        assert_equal(res.headers.get('Location'), collection_dict['id'])

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
        annotation_dict = annotation.dictize()
        assert_equal(json.loads(res.data), annotation_dict)

        # Test Location header contains Annotation IRI
        assert_equal(res.headers.get('Location'), annotation_dict['id'])