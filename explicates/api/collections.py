# -*- coding: utf8 -*-
"""Collections API module."""

from flask import request, abort
from flask.views import MethodView

from explicates.api.base import APIBase
from explicates.core import repo
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class CollectionsAPI(APIBase, MethodView):
    """Collections API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,POST,PUT,DELETE,OPTIONS,HEAD'
    }

    def _get_collection(self, collection_id):
        """Get a Collection object."""
        return self._get_domain_object(Collection, collection_id)

    def get(self, collection_id):
        """Get a Collection."""
        collection = self._get_collection(collection_id)
        items = collection.annotations
        container = self._get_container(collection, items=items)
        return self._jsonld_response(container)

    def post(self, collection_id):
        """Create an Annotation."""
        collection = self._get_collection(collection_id)
        annotation = self._create(Annotation, collection=collection)
        collection.update()
        repo.save(Collection, collection)
        extra_headers = {'Location': annotation.iri}
        return self._jsonld_response(annotation, status_code=201,
                                     headers=extra_headers)

    def put(self, collection_id):
        """Update a Collection."""
        collection = self._get_collection(collection_id)
        self._update(collection)
        items = collection.annotations
        container = self._get_container(collection, items=items)
        return self._jsonld_response(container)

    def delete(self, collection_id):
        """Delete a Collection.

        Fails if the Collection contains Annotations, or is the last one on the
        server.
        """
        collection = self._get_collection(collection_id)
        if repo.count(Collection) == 1:
            msg = 'The last collection on the server cannot be deleted'
            abort(400, msg)
        elif collection.total > 0:
            msg = 'The collection is not empty so cannot be deleted'
            abort(400, msg)
        self._delete(collection)
        return self._jsonld_response(None, status_code=204)
