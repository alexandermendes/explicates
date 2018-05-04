# -*- coding: utf8 -*-

from nose.tools import assert_equal, assert_not_equal, assert_raises
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError

from base import Test, db, with_context
from factories import CollectionFactory

from pywa.model.annotation import Annotation


class TestModelAnnotation(Test):

    def setUp(self):
        super(TestModelAnnotation, self).setUp()
        collection = CollectionFactory()
        self.annotation = Annotation(body="Simple body",
                                     target="http://example.com",
                                     collection_id=collection.id)

    @with_context
    def test_defaults(self):
        """Test Annotation is created with defaults."""
        db.session.add(self.annotation)
        db.session.add(self.annotation)
        db.session.commit()
        tmp = db.session.query(Annotation).get(1)
        assert_not_equal(tmp.slug, None)
        assert_not_equal(tmp.created, None)

    @with_context
    def test_body_is_not_nullable(self):
        """Test Annotation.body is not nullable."""
        with assert_raises(ValidationError):
            self.annotation.body = None

    @with_context
    def test_target_is_not_nullable(self):
        """Test Annotation.target is not nullable."""
        with assert_raises(ValidationError):
            self.annotation.target = None
