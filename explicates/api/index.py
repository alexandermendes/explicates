# -*- coding: utf8 -*-
"""Index API module."""

from flask import url_for, request
from flask.views import MethodView

from explicates.core import repo
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
        collections = repo.filter_by(Collection, deleted=False)
        iris = True if request.args.get('iris') == '1' else False
        container = {
            'id': url_for('api.index', _external=True),
            'label': 'All collections',
            'type': [
                'AnnotationCollection',
                'BasicContainer'
            ],
            'total': len(collections),
            'items': self._decorate_page_items(collections, iris)
        }
        return self._jsonld_response(container)

    def post(self):
        """Create an AnnotationCollection."""
        collection = self._create(Collection)
        response = self._jsonld_response(collection)
        response.headers['Location'] = collection.iri
        response.status_code = 201
        return response
