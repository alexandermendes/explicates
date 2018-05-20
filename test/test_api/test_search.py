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
    def test_with_no_results(self):
        """Test an empty AnnotationCollection is returned if no results."""
        endpoint = '/search/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search'),
            "type": [
                "AnnotationCollection",
                "BasicContainer"
            ],
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 0
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_with_results_and_no_parameters(self):
        """Test all Annotations returned when no parameters."""
        annotation = AnnotationFactory()
        endpoint = '/search/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search'),
            "type": [
                'AnnotationCollection', 
                'BasicContainer'
            ],
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', page=0),
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
    def test_search_page_with_annotations(self):
        """Test search page with Annotations."""
        annotation = AnnotationFactory()
        endpoint = '/search/?page=0'
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.search', page=0),
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
                'id': url_for('api.search'),
                'total': 1,
                'type': [
                    'AnnotationCollection',
                    'BasicContainer'
                ],
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_search_by_contains(self):
        """Test search by contains."""
        anno_data = {
            'body': 'foo',
            'target': 'bar'
        }
        anno1 = AnnotationFactory(data=anno_data)
        anno2 = AnnotationFactory()
        assert_not_equal(anno1.data.get('body'), anno2.data.get('body'))
        contains = json.dumps(anno_data)
        endpoint = '/search/?contains={}&iris=1'.format(contains)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', contains=contains, iris=1),
            "type": [
                'AnnotationCollection', 
                'BasicContainer'
            ],
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', page=0, iris=1, 
                              contains=contains),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations',
                            collection_id=anno1.collection.id,
                            annotation_id=anno1.id)
                ]
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_full_text_search(self):
        """Test full text search."""
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
        endpoint = '/search/?iris=1&fts={}'.format(fts)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', fts=fts, iris=1),
            "type": [
                'AnnotationCollection', 
                'BasicContainer'
            ],
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 2,
            'first': {
                'id': url_for('api.search', page=0, fts=fts, iris=1),
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
    def test_full_text_search_within_collection(self):
        """Test full text within collection."""
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
        endpoint = u'/search/?{}'.format(query)
        res = self.app_get_json_ld(endpoint)
        assert_equal(json.loads(res.data), {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "id": url_for('api.search', **query_dict),
            "type": [
                'AnnotationCollection', 
                'BasicContainer'
            ],
            "generated": "1984-11-19T00:00:00Z",
            'generator': current_app.config.get('GENERATOR'),
            "total": 1,
            'first': {
                'id': url_for('api.search', page=0, **query_dict),
                'type': 'AnnotationPage',
                'startIndex': 0,
                'items': [
                    url_for('api.annotations',
                            collection_id=annotation1.collection.id,
                            annotation_id=annotation1.id)
                ]
            }
        })
