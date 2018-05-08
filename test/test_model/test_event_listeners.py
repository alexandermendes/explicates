# -*- coding: utf8 -*-

import os
import json
from mock import patch, call
from nose.tools import *
from base import Test, db, with_context
from factories import CollectionFactory, AnnotationFactory

from pywa.model import event_listeners
from pywa.model.annotation import Annotation
from pywa.model.collection import Collection

class TestModelEventListeners(Test):

    def setUp(self):
        super(TestModelEventListeners, self).setUp()

    def load_schema(self, filename):
        """Load and return a JSON schema."""
        evt_dir = os.path.dirname(os.path.abspath(event_listeners.__file__))
        schemas_dir = os.path.join(os.path.dirname(evt_dir), 'schemas')
        schema_path = os.path.join(schemas_dir, filename)
        return json.load(open(schema_path))

    @with_context
    @patch('pywa.model.event_listeners.validate_json')
    def test_annotation_validated_before_insert_or_update(self, mock_validate):
        """Test that an Annotation is validated before INSERT or UPDATE."""
        annotation = AnnotationFactory(created='2018-05-08T11:03:38Z')
        inserted_dict = annotation.dictize()
        db.session.add(annotation)
        db.session.commit()

        updated_annotation = db.session.query(Annotation).get(1)
        updated_annotation.body = 'foo'
        updated_dict = updated_annotation.dictize()
        db.session.merge(updated_annotation)
        db.session.commit()

        schema = self.load_schema('annotation.json')
        assert_in(call(inserted_dict, schema), mock_validate.call_args_list)
        assert_in(call(updated_dict, schema), mock_validate.call_args_list)

    @with_context
    @patch('pywa.model.event_listeners.validate_json')
    def test_collection_validated_before_insert_or_update(self, mock_validate):
        """Test that an Collection is validated before INSERT or UPDATE."""
        collection = CollectionFactory(created='2018-05-08T11:03:38Z')
        inserted_dict = collection.dictize()
        db.session.add(collection)
        db.session.commit()

        updated_collection = db.session.query(Collection).get(1)
        updated_collection.body = 'foo'
        updated_dict = updated_collection.dictize()
        db.session.merge(updated_collection)
        db.session.commit()

        schema = self.load_schema('collection.json')
        assert_in(call(inserted_dict, schema), mock_validate.call_args_list)
        assert_in(call(updated_dict, schema), mock_validate.call_args_list)
