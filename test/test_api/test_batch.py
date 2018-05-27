# -*- coding: utf8 -*-

import json
from nose.tools import *
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory

from explicates.core import repo
from explicates.model.annotation import Annotation


class TestBatchAPI(Test):

    def setUp(self):
        super(TestBatchAPI, self).setUp()

    @with_context
    def test_batch_delete_annotations(self):
        """Test batch delete Annotations."""
        annotations = AnnotationFactory.create_batch(3)
        data = [anno.dictize() for anno in annotations]
        endpoint = '/batch/'
        res = self.app_delete_json_ld(endpoint, data=data)
        assert_equal(res.status_code, 204, res.data)
        annotations_after = repo.filter_by(Annotation, deleted=False)
        assert_equal(annotations_after, [])

    @with_context
    def test_batch_delete_with_invalid_annotations(self):
        """Test batch delete with invalid Annotations."""
        data = [{
            'id': 'foo'
        }]
        endpoint = '/batch/'
        res = self.app_delete_json_ld(endpoint, data=data)
        assert_equal(res.status_code, 400, res.data)
        err_msg = ('400 Bad Request: The query contains IDs that cannot be '
                   'found in the database')
        assert_equal(json.loads(res.data)['message'], err_msg, res.data)

    @with_context
    def test_batch_delete_annotations_with_no_data(self):
        """Test batch delete Annotations with no data."""
        endpoint = '/batch/'
        res = self.app_delete_json_ld(endpoint)
        assert_equal(res.status_code, 400, res.data)

    @with_context
    def test_batch_delete_annotations_with_invalid_data(self):
        """Test batch delete Annotations with invalid data."""
        endpoint = '/batch/'
        data = dict(foo='bar')
        res = self.app_delete_json_ld(endpoint, data=data)
        assert_equal(res.status_code, 400, res.data)
