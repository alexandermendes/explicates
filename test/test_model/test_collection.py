# -*- coding: utf8 -*-

from flask import current_app, url_for
from mock import patch
from nose.tools import assert_equal, assert_raises
from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError
try:
    from urllib import quote
except ImportError:  # py3
    from urllib.parse import quote

from base import Test, db, with_context

from pywa.model.collection import Collection


class TestModelCollection(Test):

    def setUp(self):
        super(TestModelCollection, self).setUp()
        self.collection = Collection(slug="foo",
                                     label="My Collection")

    @with_context
    def test_id_added(self):
        """Test Collection.id is added."""
        db.session.add(self.collection)
        db.session.commit()
        tmp = db.session.query(Collection).get(1)
        root_url = url_for('api.index')
        collection_slug = quote(self.collection.slug.encode('utf8'))
        expected = '{}{}'.format(root_url, collection_slug)
        assert_equal(tmp.id, expected)
