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
