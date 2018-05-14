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


class TestSearchAPI(Test):

    def setUp(self):
        super(TestSearchAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    @with_context
    def test_404_when_invalid_domain_object(self):
        """Test 404 when domain object is invalid."""
        endpoint = '/search/foo/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    @freeze_time("1984-11-19")
    def test_all_valid_domain_objects_returned(self):
        """Test an OrderedCollection is returned for all valid objects."""
        tables = ['annotation', 'collection']
        for table in tables:
            endpoint = '/search/{}/'.format(table)
            res = self.app_get_json_ld(endpoint)
            assert_equal(json.loads(res.data), {
                "@context": "http://www.w3.org/ns/anno.jsonld",
                "id": url_for('api.search', tablename=table),
                "type": "OrderedCollection",
                "generated": "1984-11-19T00:00:00Z",
                'generator': current_app.config.get('GENERATOR'),
                "total": 0
            })

    @with_context
    @freeze_time("1984-11-19")
    def test_ordered_collection_with_annotations(self):
        """Test OrderedCollection with Annotations."""
        annotation = AnnotationFactory()
        endpoint = '/search/annotation/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', tablename='annotation'),
            "type": "OrderedCollection",
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', tablename='annotation', page=0),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    {
                        'id': url_for('api.annotations',
                                      collection_id=annotation.collection.id,
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
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_ordered_collection_with_annotation_collections(self):
        """Test OrderedCollection with AnnotationCollections."""
        collection = CollectionFactory()
        endpoint = '/search/collection/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', tablename='collection'),
            "type": "OrderedCollection",
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', tablename='collection', page=0),
                'type': 'OrderedCollectionPage',
                'startIndex': 0,
                'items': [
                    {
                        'id': url_for('api.collections',
                                      collection_id=collection.id),
                        'type': collection.data['type'],
                        'created': '1984-11-19T00:00:00Z',
                        'generated': '1984-11-19T00:00:00Z',
                        'generator': current_app.config.get('GENERATOR'),
                        'total': 0
                    }
                ]
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_search_page_with_annotations(self):
        """Test search page with Annotations."""
        annotation = AnnotationFactory()
        endpoint = '/search/annotation/?page=0'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.search', tablename='annotation', page=0),
            'type': 'AnnotationPage',
            'startIndex': 0,
            'items': [
                {
                    'id': url_for('api.annotations',
                                    collection_id=annotation.collection.id,
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
                'id': url_for('api.search', tablename='annotation'),
                'total': 1,
                'type': 'OrderedCollection',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_search_page_with_annotation_collections(self):
        """Test search page with AnnotationCollections."""
        collection = CollectionFactory()
        endpoint = '/search/collection/?page=0'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.search', tablename='collection', page=0),
            'type': 'OrderedCollectionPage',
            'startIndex': 0,
            'items': [
                {
                    'id': url_for('api.collections',
                                  collection_id=collection.id),
                    'type': collection.data['type'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'generator': current_app.config.get('GENERATOR'),
                    'total': 0
                }
            ],
            'partOf': {
                'id': url_for('api.search', tablename='collection'),
                'total': 1,
                'type': 'OrderedCollection',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_search_by_contains_for_annotation_collections(self):
        """Test search by contains for AnnotationCollections."""
        collection1 = CollectionFactory(data={
            'type': ['AnnotationCollection', 'BasicContainer'],
            'label': 'foo'
        })
        collection2 = CollectionFactory()
        assert_not_equal(collection2.data.get('label'), 'foo')
        contains = json.dumps({"label": "foo"})
        endpoint = '/search/collection/?contains={}'.format(contains)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', tablename='collection',
                          contains=contains),
            "type": "OrderedCollection",
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', tablename='collection', page=0,
                              contains=contains),
                'type': 'OrderedCollectionPage',
                'startIndex': 0,
                'items': [
                    {
                        'id': url_for('api.collections',
                                      collection_id=collection1.id),
                        'type': collection1.data['type'],
                        'label': collection1.data['label'],
                        'created': '1984-11-19T00:00:00Z',
                        'generated': '1984-11-19T00:00:00Z',
                        'generator': current_app.config.get('GENERATOR'),
                        'total': 0
                    }
                ]
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_full_text_search_for_annotations(self):
        """Test full text search for Annotations."""
        annotation1 = AnnotationFactory(data={
            'type': 'Annotation',
            'body': 'foo',
            'target': 'bar'
        })
        annotation2 = AnnotationFactory(data={
            'type': 'Annotation',
            'body': {
                'value': 'foo'
            },
            'target': {
                'source': 'baz'
            }
        })
        AnnotationFactory(data={
            'type': 'Annotation',
            'body': 'qux',
            'target': 'foo'
        })

        fts = 'body::foo'
        endpoint = '/search/annotation/?iris=1&fts={}'.format(fts)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', tablename='annotation', fts=fts,
                          iris=1),
            "type": "OrderedCollection",
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 2,
            'first': {
                'id': url_for('api.search', tablename='annotation', page=0,
                              fts=fts, iris=1),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations',
                            collection_id=annotation1.collection.id,
                            annotation_id=annotation1.id),
                    url_for('api.annotations',
                            collection_id=annotation2.collection.id,
                            annotation_id=annotation2.id)
                ]
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_full_text_search_within_category_for_annotations(self):
        """Test full text within category for Annotations."""
        collection1 = CollectionFactory()
        collection2 = CollectionFactory()
        annotation1 = AnnotationFactory(data={
            'type': 'Annotation',
            'body': 'foo',
            'target': 'bar'
        }, collection=collection1)
        AnnotationFactory(data={
            'type': 'Annotation',
            'body': {
                'value': 'foo'
            },
            'target': {
                'source': 'baz'
            }
        }, collection=collection2)
        AnnotationFactory(data={
            'type': 'Annotation',
            'body': 'qux',
            'target': 'foo'
        })

        fts = 'body::foo'
        query = u'iris=1&fts={0}&collection.id={1}'.format(fts, collection1.id)
        query_dict = {'fts': fts, 'iris': 1, 'collection.id': collection1.id}
        endpoint = u'/search/annotation/?{}'.format(query)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', tablename='annotation', **query_dict),
            "type": "OrderedCollection",
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', tablename='annotation', page=0,
                              **query_dict),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations',
                            collection_id=annotation1.collection.id,
                            annotation_id=annotation1.id)
                ]
            }
        })
