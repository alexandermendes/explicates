# -*- coding: utf8 -*-

import json
from rdflib import *
from flask import request, jsonify, Response, abort

from libanno.model.base import BaseDomainObject


class ContextualResponse(Response):
    """Custom response class."""

    @classmethod
    def force_type(cls, rv, environ=None):
        """Convert response data to JSON by default."""
        if isinstance(rv, BaseDomainObject):
            rv = rv.dictize()
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(ContextualResponse, cls).force_type(rv, environ)
