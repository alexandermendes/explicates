# -*- coding: utf8 -*-

from flask import current_app
from mock import patch
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError

from base import Test, db, with_context

from pywa.model.collection import Collection


class TestModelCollection(Test):

    def setUp(self):
        super(TestModelCollection, self).setUp()
        self.collection = Collection(slug="foo",
                                     label="My Collection")

    @with_context
    def test_get_id_suffix(self):
        """Test Collection id suffix."""
        id_suffix = self.collection.get_id_suffix()
        assert_equal(id_suffix, self.collection.slug)

    @with_context
    def test_get_extra_info(self):
        """Test Collection extra info."""
        extra_info = self.collection.get_extra_info()
        assert_dict_equal(extra_info, {
            'type': 'AnnotationCollection'
        })