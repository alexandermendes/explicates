# -*- coding: utf8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for


class TestIndexAPI(Test):

    def setUp(self):
        super(TestIndexAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    @with_context
    @freeze_time("1984-11-19")
    def test_list_all_collections(self):
        """Test a list of all Annotation Collections is returned."""
        collection1 = CollectionFactory()
        collection2 = CollectionFactory()
        AnnotationFactory.create_batch(3, collection=collection1)
        expected = {
            '@context': 'http://www.w3.org/ns/anno.jsonld',
            'id': url_for('api.index', _external=True),
            'label': 'All collections',
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ],
            'total': 2,
            'items': [
                {
                    'id': url_for('api.collections',
                                  collection_id=collection1.id,
                                  _external=True),
                    'type': collection1.data['type'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'total': 3
                },
                {
                    'id': url_for('api.collections',
                                  collection_id=collection2.id,
                                  _external=True),
                    'type': collection2.data['type'],
                    'created': '1984-11-19T00:00:00Z',
                    'generated': '1984-11-19T00:00:00Z',
                    'total': 0
                }
            ]
        }

        endpoint = '/annotations/'
        res = self.app_get_json_ld(endpoint)
        data = json.loads(res.data.decode('utf8'))
        assert_dict_equal(data, expected)
