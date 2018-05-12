# -*- coding: utf8 -*-

from flask import current_app
from mock import patch
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError

from base import Test, db, with_context

from explicates.model.collection import Collection


class TestModelCollection(Test):

    def setUp(self):
        super(TestModelCollection, self).setUp()

    @with_context
    def test_get_id_suffix(self):
        """Test Collection id suffix."""
        collection = Collection()
        id_suffix = collection.get_id_suffix()
        assert_equal(id_suffix, '{}/'.format(collection.slug))
