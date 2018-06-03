# -*- coding: utf8 -*-
"""Search API module."""

import json
from flask import abort, request
from flask.views import MethodView
from sqlalchemy.exc import ProgrammingError

from explicates.core import search
from explicates.api.base import APIBase
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class SearchAPI(APIBase, MethodView):
    """Search API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,OPTIONS,HEAD'
    }

    def _filter_valid_params(self, data):
        """Return the valid search parameters."""
        valid_keys = ['contains', 'collection', 'fts', 'fts_phrase', 'limit',
                      'range', 'order_by', 'offset']
        return {k: v for k, v in data.items() if k in valid_keys}

    def get(self):
        """Search Annotations."""
        data = request.args.to_dict(flat=True)
        if request.data:
            data = json.loads(request.data.decode('utf8'))
        params = self._filter_valid_params(data)

        try:
            results = search.search(**params)
        except (ValueError, ProgrammingError) as err:
            abort(400, err)

        tmp_collection = Collection(data={
            "type": [
                "AnnotationCollection",
                "BasicContainer"
            ]
        })
        container = self._get_container(tmp_collection, items=results,
                                        total=len(results), **params)
        return self._jsonld_response(container)
