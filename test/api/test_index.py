# -*- coding: utf8 -*-

import json
from nose.tools import assert_equal

from base import Test, with_context
from factories import CollectionFactory

from pywa.core import collection_repo


class TestApiIndex(Test):

    def setUp(self):
        super(TestApiIndex, self).setUp()

    @with_context
    def test_collection_not_found(self):
        """Test Collection not found."""
        endpoint = '/foo'
        res = self.app_get_json(endpoint)
        assert_equal(res.status_code, 404)

    @with_context
    def test_collection_found(self):
        """Test Collection found."""
        slug = 'foo'
        collection = CollectionFactory(slug=slug)
        endpoint = '/{}'.format(slug)
        res = self.app_get_json(endpoint)
        assert_equal(res.status_code, 200)
