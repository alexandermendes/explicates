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
