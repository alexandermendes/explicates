# -*- coding: utf8 -*-
"""Index API module."""

from flask.views import MethodView

from explicates.api.base import APIBase
from explicates.model.collection import Collection


class IndexAPI(APIBase, MethodView):
    """Index API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,POST,OPTIONS,HEAD'
    }

    def get(self):
        """Return a list of all AnnotationCollections."""
        pass

    def post(self):
        """Create an AnnotationCollection."""
        collection = self._create(Collection)
        response = self._jsonld_response(collection)
        response.headers['Location'] = collection.iri
        response.status_code = 201
        return response
