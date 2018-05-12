# -*- coding: utf8 -*-

from nose.tools import *
from base import Test, with_context

from factories import CollectionFactory


class TestCors(Test):

    def setUp(self):
        super(TestCors, self).setUp()

    @with_context
    def test_origin(self):
        """Test CORS Access-Control-Allow-Origin."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}'.format(collection.id)
        headers = {
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        res = self.app.options(endpoint, headers=headers)
        assert_equal(res.headers['Access-Control-Allow-Origin'] ,'*')

    @with_context
    def test_methods(self):
        """Test CORS Access-Control-Allow-Methods."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}'.format(collection.id)
        headers = {
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        res = self.app.options(endpoint, headers=headers)
        print res.headers
        methods = ['PUT', 'HEAD', 'DELETE', 'OPTIONS', 'GET']
        assert_not_equal(res.headers.get('Access-Control-Allow-Methods'), None)
        for m in methods:
            assert_in(m, res.headers['Access-Control-Allow-Methods'])

    @with_context
    def test_max_age(self):
        """Test CORS Access-Control-Max-Age."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}'.format(collection.id)
        headers = {
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        res = self.app.options(endpoint, headers=headers)
        assert_equal(res.headers.get('Access-Control-Max-Age'), '21600')

    @with_context
    def test_headers(self):
        """Test CORS headers."""
        collection = CollectionFactory()
        endpoint = u'/annotations/{}'.format(collection.id)
        test_headers = ['Content-Type', 'Authorization']
        for hdr in test_headers:
            headers = {
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': hdr
            }
            res = self.app.options(endpoint, headers=headers)
            assert_equal(res.headers.get('Access-Control-Allow-Headers'), hdr)
