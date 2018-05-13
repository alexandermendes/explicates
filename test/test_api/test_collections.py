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


class TestCollectionsAPI(Test):

    def setUp(self):
        super(TestCollectionsAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

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
        data = dict(type=['AnnotationCollection', 'BasicContainer'],
                    label='foo')
        res = self.app_post_json_ld(endpoint, data=data)
        collection = repo.get(Collection, 1)
        assert_not_equal(collection, None)

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
    def test_collection_created_with_slug(self):
        """Test Collection created with slug."""
        endpoint = '/annotations/'
        data = dict(type=['AnnotationCollection', 'BasicContainer'])
        slug = 'bar'
        headers = dict(slug=slug)
        res = self.app_post_json_ld(endpoint, data=data, headers=headers)
        collection = repo.get(Collection, 1)
        assert_equal(collection.id, slug)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_default_container(self):
        """Test get Collection with default container preferences.

        Should default to PreferContainedDescriptions.
        """
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': {
                'id': url_for('api.collections', collection_id=collection.id,
                              page=0),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    {
                        'id': url_for('api.annotations',
                                      collection_id=collection.id,
                                      annotation_id=annotation.id),
                        'type': 'Annotation',
                        'body': annotation.data['body'],
                        'target': annotation.data['target'],
                        'created': '1984-11-19T00:00:00Z',
                        'generated': '1984-11-19T00:00:00Z',
                        'generator': current_app.config.get('GENERATOR')
                    }
                ]
            }
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_default_container_with_multiple_pages(self):
        """Test Collection with default container and multiple pages."""
        collection = CollectionFactory()
        n_pages = 3
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = n_pages - 1
        annotations = AnnotationFactory.create_batch(per_page * n_pages,
                                                     collection=collection)

        items = []
        for anno in annotations[:per_page]:
            items.append(
                {
                    'id': url_for('api.annotations',
                                    collection_id=collection.id,
                                    annotation_id=anno.id),
                    'type': 'Annotation',
                    'body': anno.data['body'],
                    'target': anno.data['target'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'generator': current_app.config.get('GENERATOR')
                }
            )

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections',
                          collection_id=collection.id),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': len(annotations),
            'first': {
                'id': url_for('api.collections', collection_id=collection.id,
                              page=0),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': items,
                'next': url_for('api.collections', collection_id=collection.id,
                                page=1),
            },
            'last': url_for('api.collections',
                            collection_id=collection.id, page=last_page)
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_iri_container(self):
        """Test get Collection with PreferContainedIRIs."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          iris=1),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': {
                'id': url_for('api.collections', collection_id=collection.id,
                              **dict(page=0, iris=1)),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations', collection_id=collection.id,
                            annotation_id=annotation.id)
                ]
            }
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        prefer = ('return=representation;include='
                  '"http://www.w3.org/ns/oa#PreferContainedIRIs"')
        headers = dict(prefer=prefer)
        res = self.app_get_json_ld(endpoint, headers=headers)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_iri_container_using_query_string(self):
        """Test get Collection with PreferContainedIRIs using query."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          iris=1),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': {
                'id': url_for('api.collections', collection_id=collection.id,
                              **dict(page=0, iris=1)),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations', collection_id=collection.id,
                            annotation_id=annotation.id)
                ]
            }
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint + '?iris=1')
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_minimal_container(self):
        """Test get Collection with PreferMinimalContainer."""
        collection = CollectionFactory()
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
        prefer = ('return=representation;include='
                  '"http://www.w3.org/ns/ldp#PreferMinimalContainer"')
        headers = dict(prefer=prefer)
        res = self.app_get_json_ld(endpoint, headers=headers)
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_minimal_container_with_iris(self):
        """Test get Collection with PreferMinimalContainer and IRIs."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          iris=1),
            'type': collection.data['type'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': url_for('api.collections',
                             collection_id=collection.id,
                             **dict(page=0, iris=1))
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        prefer = ('return=representation;include='
                  '"http://www.w3.org/ns/ldp#PreferMinimalContainer'
                  ' http://www.w3.org/ns/oa#PreferContainedIRIs"')
        headers = dict(prefer=prefer)
        res = self.app_get_json_ld(endpoint, headers=headers)
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
        """Test Collection updated.

        The default container representation should be returned.
        """
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)
        data = collection.dictize().copy()
        data['label'] = "My new label"
        assert_equal(collection.modified, None)

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_put_json_ld(endpoint, data=data)

        # Test object updated
        assert_equal(collection.modified, '1984-11-19T00:00:00Z')

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id),
            'type': data['type'],
            'label': data['label'],
            'created': '1984-11-19T00:00:00Z',
            'generated': '1984-11-19T00:00:00Z',
            'modified': '1984-11-19T00:00:00Z',
            'generator': current_app.config.get('GENERATOR'),
            'total': 1,
            'first': {
                'id': url_for('api.collections', collection_id=collection.id,
                              page=0),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    {
                        'id': url_for('api.annotations',
                                      collection_id=collection.id,
                                      annotation_id=annotation.id),
                        'type': 'Annotation',
                        'body': annotation.data['body'],
                        'target': annotation.data['target'],
                        'created': '1984-11-19T00:00:00Z',
                        'generated': '1984-11-19T00:00:00Z',
                        'generator': current_app.config.get('GENERATOR')
                    }
                ]
            }
        }

        # Test data
        assert_equal(json.loads(res.data), expected)

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

    @with_context
    @freeze_time("1984-11-19")
    def test_get_page(self):
        """Test get AnnotationPage."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          page=0),
            'type': 'AnnotationPage',
            'startIndex': 0,
            'items': [
                {
                    'id': url_for('api.annotations',
                                    collection_id=collection.id,
                                    annotation_id=annotation.id),
                    'type': 'Annotation',
                    'body': annotation.data['body'],
                    'target': annotation.data['target'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'generator': current_app.config.get('GENERATOR')
                }
            ],
            'partOf': {
                'id': url_for('api.collections', collection_id=collection.id),
                'total': 1,
                'type': [
                    'BasicContainer',
                    'AnnotationCollection'
                ],
                'created': '1984-11-19T00:00:00Z',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint + '?page=0')
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_multiple_pages(self):
        """Test get multiple AnnotationPage."""
        collection = CollectionFactory()
        n_pages = 3
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = n_pages - 1
        annotations = AnnotationFactory.create_batch(per_page * n_pages,
                                                     collection=collection)

        current_page = 1
        items = []
        for anno in annotations[current_page:current_page + per_page]:
            items.append(
                {
                    'id': url_for('api.annotations',
                                    collection_id=collection.id,
                                    annotation_id=anno.id),
                    'type': 'Annotation',
                    'body': anno.data['body'],
                    'target': anno.data['target'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'generator': current_app.config.get('GENERATOR')
                }
            )

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          page=current_page),
            'type': 'AnnotationPage',
            'startIndex': 0,
            'items': items,
            'partOf': {
                'id': url_for('api.collections', collection_id=collection.id),
                'total': len(annotations),
                'type': [
                    'BasicContainer',
                    'AnnotationCollection'
                ],
                'created': '1984-11-19T00:00:00Z',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            },
            'next': url_for('api.collections', collection_id=collection.id,
                            page=current_page + 1),
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint + '?page={}'.format(current_page))
        assert_equal(json.loads(res.data), expected)

    @with_context
    @freeze_time("1984-11-19")
    def test_get_page_with_iris(self):
        """Test get AnnotationPage with IRIs."""
        collection = CollectionFactory()
        annotation = AnnotationFactory(collection=collection)

        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.collections', collection_id=collection.id,
                          **dict(page=0, iris=1)),
            'type': 'AnnotationPage',
            'startIndex': 0,
            'items': [
                url_for('api.annotations', collection_id=collection.id,
                        annotation_id=annotation.id)
            ],
            'partOf': {
                'id': url_for('api.collections', collection_id=collection.id,
                              iris=1),
                'total': 1,
                'type': [
                    'BasicContainer',
                    'AnnotationCollection'
                ],
                'created': '1984-11-19T00:00:00Z',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        }

        endpoint = u'/annotations/{}/'.format(collection.id)
        res = self.app_get_json_ld(endpoint + '?page=0&iris=1')
        assert_equal(json.loads(res.data), expected)
