# -*- coding: utf8 -*-

from flask import current_app
from mock import patch
from nose.tools import *
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError

from base import Test, db, with_context
from factories import CollectionFactory

from pywa.model.annotation import Annotation


class TestModelAnnotation(Test):

    def setUp(self):
        super(TestModelAnnotation, self).setUp()

    @with_context
    def test_defaults(self):
        """Test Annotation is created with defaults."""
        annotation = Annotation(body="Simple body",
                                target="http://example.com")
        db.session.add(annotation)
        db.session.commit()
        tmp = db.session.query(Annotation).get(1)
        assert_not_equal(tmp.slug, None)
        assert_not_equal(tmp.created, None)

    @with_context
    def test_get_id_suffix(self):
        """Test Annotation id suffix."""
        collection = CollectionFactory()
        annotation = Annotation(collection=collection)
        expected = u'{}/{}'.format(collection.slug, annotation.slug)
        id_suffix = annotation.get_id_suffix()
        assert_equal(id_suffix, expected)

    @with_context
    @patch('pywa.model.annotation.make_timestamp')
    def test_get_extra_info(self, mock_ts):
        """Test Annotation extra info."""
        annotation = Annotation()
        fake_ts = 'foo'
        mock_ts.return_value = fake_ts
        extra_info = annotation.get_extra_info()
        assert_dict_equal(extra_info, {
            'type': 'Annotation',
            'generated': fake_ts,
            'generator': current_app.config.get('GENERATOR')
        })
