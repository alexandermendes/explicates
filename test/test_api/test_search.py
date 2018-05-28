# -*- coding: utf8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for


class TestSearchAPI(Test):

    def setUp(self):
        super(TestSearchAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    @with_context
    @freeze_time("1984-11-19")
    def test_search(self):
        """Test search."""
        endpoint = '/search/'
        anno_data = dict(body='foo', target='bar', type='Annotation')
        anno = AnnotationFactory(data=anno_data)
        AnnotationFactory()
        query = {
            'contains': {
                'body': anno_data['body']
            }
        }
        res = self.app_get_json_ld(endpoint, data=query)
        assert_dict_equal(json.loads(res.data), {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id':  url_for('api.search', **query),
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ],
            'generated': '1984-11-19T00:00:00Z',
            'total': 1,
            'first': {
                'id': url_for('api.search', page=0, **query),
                'type': 'AnnotationPage',
                'items': [
                    {
                        'id': url_for('api.annotations',
                                    collection_id=anno.collection.id,
                                    annotation_id=anno.id),
                        'type': 'Annotation',
                        'body': anno.data['body'],
                        'target': anno.data['target'],
                        'created': '1984-11-19T00:00:00Z',
                        'generated': '1984-11-19T00:00:00Z',
                        'generator': current_app.config.get('GENERATOR')
                    }
                ],
                'startIndex': 0
            }
        })

    @with_context
    @freeze_time("1984-11-19")
    def test_search_with_bad_query(self):
        """Test search with bad query."""
        endpoint = '/search/'
        query = {
            'fts': {
                'body': 'foo'
            }
        }
        res = self.app_get_json_ld(endpoint, data=query)
        assert_equal(res.status_code, 400, res.data)
