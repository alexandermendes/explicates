# -*- coding: utf8 -*-

from flask import current_app
from mock import patch
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError

from base import Test, db, with_context
from factories import CollectionFactory

from explicates.model.annotation import Annotation


class TestModelAnnotation(Test):

    def setUp(self):
        super(TestModelAnnotation, self).setUp()

    @with_context
    def test_get_id_suffix(self):
        """Test Annotation id suffix."""
        collection = CollectionFactory()
        annotation = Annotation(collection=collection)
        expected = u'{}/{}/'.format(collection.id, annotation.id)
        id_suffix = annotation.get_id_suffix()
        assert_equal(id_suffix, expected)
