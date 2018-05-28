# -*- coding: utf8 -*-

import json
from nose.tools import *
from base import Test, with_context
from factories import CollectionFactory, AnnotationFactory
from flask import current_app, url_for

from explicates.core import repo
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation
from explicates.api.base import APIBase


class TestBaseAPI(Test):

    def setUp(self):
        super(TestBaseAPI, self).setUp()
        self.api_base = APIBase()

    @with_context
    def test_slice_annotations(self):
        """Test first slice of Annotations returned."""
        collection = CollectionFactory()
        annotations = AnnotationFactory.create_batch(4, collection=collection)
        out = self.api_base._slice_annotations(collection.annotations, 2, 0)
        assert_equal(out, annotations[:2])

    @with_context
    def test_offset_slice_annotations(self):
        """Test offset slice of Annotations returned."""
        collection = CollectionFactory()
        annotations = AnnotationFactory.create_batch(4, collection=collection)
        out = self.api_base._slice_annotations(collection.annotations, 2, 1)
        assert_equal(out, annotations[2:])

    @with_context
    def test_get_iri_with_unknown_object(self):
        """Test get IRI with unknown object."""
        assert_raises(TypeError, self.api_base._get_iri, {})

    @with_context
    def test_get_json_reponse_with_unknown_object(self):
        """Test get JSON response with unknown object."""
        assert_raises(TypeError, self.api_base._jsonld_response, [42])
