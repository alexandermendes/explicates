# -*- coding: utf8 -*-
"""Search API module."""

from flask import abort, request
from flask.views import MethodView

from explicates.core import repo
from explicates.api.base import APIBase
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation
from explicates.model.ordered_collection import OrderedCollection


class SearchAPI(APIBase, MethodView):
    """Search API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,OPTIONS,HEAD'
    }

    def _get_model(self, tablename):
        """Return a model by table name."""
        mapping = {
            'annotation': Annotation,
            'collection': Collection
        }
        return mapping.get(tablename)

    def get(self, tablename):
        """Search for domain objects by table name."""
        model_cls = self._get_model(tablename)
        if not model_cls:
            abort(404)

        contains = request.args.get('contains')
        fts = request.args.get('fts')

        try:
            results = repo.search(model_cls, contains=contains, fts=fts)
        except ValueError as err:
            abort(400, err.message)

        tmp_collection = OrderedCollection(tablename, results, 'api.search')
        container = self._get_container(tmp_collection, items=results)
        return self._jsonld_response(container)
