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
        print res.data
        assert_equal(res.status_code, 404)

    # @with_context
    # def test_valid_domain_objects_returned(self):
    #     """Test a Collection is returned for all valid domain objects."""
    #     domain_objects = ['annotation', 'collection']
    #     for do in domain_objects:
    #         endpoint = '/search/{}/'.format(do)
    #         res = self.app_get_json_ld(endpoint)
    #         assert_equal(json.loads(res.data), {
    #             "@context": "https://www.w3.org/ns/activitystreams.jsonld",
    #             "id": "http://example.org/search/{}/".format(do),
    #             "type": "Collection",
    #             "totalItems": 0
    #         })
