# -*- coding: utf8 -*-
"""Search API module."""

from flask import abort
from flask.views import MethodView

from explicates.api.base import APIBase
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class SearchAPI(APIBase, MethodView):
    """Search API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,OPTIONS,HEAD'
    }

    def _get_model(self, domain_object):
        """Get the model from a string."""
        models = {
            'collection': Collection,
            'annotation': Annotation
        }
        return models.get(domain_object.lower())

    def _get_container(self):
        {
            "@context": "https://www.w3.org/ns/activitystreams.jsonld",
            "id": "http://example.org/search/collection/?query=foo",
            "type": "Collection",
            "totalItems": 42023,
            "first": "http://example.org/search/collection/?page=0&query=foo",
            "last": "http://example.org/search/collection/?page=42&query=foo"
        }

    def get(self, domain_object):
        """Search for a domain object."""
        model = self._get_model(domain_object)
        if not model:
            abort(404)

        return self._create_response(None)
