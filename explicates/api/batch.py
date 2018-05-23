# -*- coding: utf8 -*-
"""Batch API module."""

import json
from flask import request, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

try:
    from urllib import unquote
except ImportError:  # py3
    from urllib.parse import unquote

from explicates.core import repo
from explicates.api.base import APIBase
from explicates.model.annotation import Annotation


class BatchAPI(APIBase, MethodView):
    """Batch API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'DELETE,OPTIONS,HEAD'
    }

    def _get_base_id(self, annotation):
        """Return the base ID extracted from the full IRI."""
        iri = annotation.get('id')
        if not iri:
            abort(400, 'Invalid Annotation passed in request')
        return unquote(iri).rstrip('/').split('/')[-1]

    def delete(self):
        """Batch delete items."""
        if not request.data:
            abort(400)
        json_data = json.loads(request.data)
        if type(json_data) != list:
            abort(400)
        annotation_ids = [self._get_base_id(anno) for anno in json_data]
        try:
            repo.batch_delete(Annotation, annotation_ids)
        except (IntegrityError, ValueError) as err:
            abort(400, err.message)
        return self._jsonld_response(None, status_code=204)
