# -*- coding: utf8 -*-
"""Annotations API module."""

from flask.views import MethodView

from explicates.api.base import APIBase
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class AnnotationsAPI(APIBase, MethodView):
    """Annotations API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,PUT,DELETE,OPTIONS,HEAD'
    }

    def _get_annotation(self, collection_id, annotation_id):
        """Return an Annotation object."""
        collection = self._get_domain_object(Collection, collection_id)
        annotation = self._get_domain_object(Annotation, annotation_id,
                                             collection=collection)
        return annotation

    def get(self, collection_id, annotation_id):
        """Get an Annotation."""
        annotation = self._get_annotation(collection_id, annotation_id)
        return self._jsonld_response(annotation)

    def put(self, collection_id, annotation_id):
        """Update an Annotation."""
        annotation = self._get_annotation(collection_id, annotation_id)
        self._update(annotation)
        return self._jsonld_response(annotation)

    def delete(self, collection_id, annotation_id):
        """Delete an Annotation."""
        annotation = self._get_annotation(collection_id, annotation_id)
        self._delete(annotation)
        return self._jsonld_response(None, status_code=204)
