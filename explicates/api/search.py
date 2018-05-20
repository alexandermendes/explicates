# -*- coding: utf8 -*-
"""Search API module."""

from flask import abort, request
from flask.views import MethodView
from sqlalchemy.exc import ProgrammingError

from explicates.core import repo
from explicates.api.base import APIBase
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class SearchAPI(APIBase, MethodView):
    """Search API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,OPTIONS,HEAD'
    }

    def _get_valid_filters(self):
        """Return valid filters."""
        filters = {}
        for k in request.args.keys():
            if k not in ['page', 'iris', 'fts', 'contains']:
                try:
                    getattr(Annotation, k)
                except AttributeError as err:
                    # Full-stops used to model relationships
                    if len(k.split('.')) == 2:
                        filters[k] = request.args[k]
                    else:
                        abort(415, err.message)
                filters[k] = request.args[k]
        return filters

    def get(self):
        """Search Annotations."""
        filters = self._get_valid_filters()
        filters['contains'] = request.args.get('contains')
        filters['fts'] = request.args.get('fts')
        print 'foo'
        try:
            results = repo.search(Annotation, **filters)
        except (ValueError, ProgrammingError) as err:
            abort(400, err.message)

        tmp_collection = Collection(data={
            "type": [
                "AnnotationCollection",
                "BasicContainer"
            ],
            "total": len(results)
        })
        container = self._get_container(tmp_collection, items=results)
        return self._jsonld_response(container)
