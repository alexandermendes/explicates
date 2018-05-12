# -*- coding: utf8 -*-
"""Annotations API module."""

from flask.views import MethodView

from explicates.core import annotation_repo, collection_repo
from explicates.api.base import APIBase


class AnnotationsAPI(APIBase, MethodView):
    """Annotations API class."""

    common_headers = {
        'Allow': 'GET,PUT,DELETE,OPTIONS,HEAD'
    }

    def _get_annotation(self, collection_id, annotation_id):
        collection = self._get_domain_object(collection_repo, collection_id)
        annotation = self._get_domain_object(annotation_repo, annotation_id,
                                             collection=collection)
        return annotation

    def get(self, collection_id, annotation_id):
        annotation = self._get_annotation(collection_id, annotation_id)
        return self._create_response(annotation)

    def put(self, collection_id, annotation_id):
        annotation = self._get_annotation(collection_id, annotation_id)
        return self._update(annotation, annotation_repo)

    def delete(self, collection_id, annotation_id):
        annotation = self._get_annotation(collection_id, annotation_id)
        return self._delete(annotation, annotation_repo)
