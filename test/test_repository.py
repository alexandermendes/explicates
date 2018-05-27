# -*- coding: utf8 -*-

from nose.tools import *
from base import Test

from explicates.core import repo
from explicates.model.annotation import Annotation
from explicates.model.collection import Collection


class TestRepository(Test):

    def setUp(self):
        super(TestRepository, self).setUp()

    def test_wrong_object_not_saved(self):
        """Test that the wrong object cannot be saved."""
        annotation = Annotation(data={
            'body': 'foo',
            'target': 'bar'
        })
        assert_raises(ValueError, repo.save, Collection, annotation)

    def test_wrong_object_not_updated(self):
        """Test that the wrong object cannot be updated."""
        annotation = Annotation(data={
            'body': 'foo',
            'target': 'bar'
        })
        assert_raises(ValueError, repo.update, Collection, annotation)
