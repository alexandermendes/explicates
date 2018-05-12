# -*- coding: utf8 -*-
"""Collections API module."""

from flask import url_for, current_app, request, abort
from flask.views import MethodView

from explicates.model.annotation import Annotation
from explicates.core import collection_repo, annotation_repo
from explicates.api.base import APIBase


class CollectionsAPI(APIBase, MethodView):
    """Collections API class."""

    common_headers = {
        'Allow': 'GET,POST,PUT,DELETE,OPTIONS,HEAD'
    }

    def _get_collection(self, collection_id):
        """Get a Collection object."""
        collection = self._get_domain_object(collection_repo, collection_id)
        return collection

    def _get_last_page(self, collection):
        """Get the last page number for a Collection.

        Pagination is zero-based.
        """
        count = len(collection.annotations)
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = 0 if count <= 0 else (count - 1) // per_page
        return last_page

    def _get_page_links(self, collection):
        """Add page links to a Collection."""
        kwargs = request.args.copy()
        kwargs.pop('page', None)

        links = {}
        if collection.annotations:
            links['first'] = url_for('api.collections', _external=True, page=0,
                                     collection_id=collection.id, **kwargs)

        last_p = self._get_last_page(collection)
        if last_p > 0:
            links['last'] = url_for('api.collections', _external=True,
                                    page=last_p, collection_id=collection.id,
                                    **kwargs)

        return links

    def _get_page(collection, page, query_str):
        """Respond with a Page of a Collection."""
        collection_dict = collection.dictize()
        page_iri = "{0}/{1}".format(collection_dict['id'], page)
        next_iri = "{0}/{1}".format(collection_dict['id'], page + 1)

        if query_str:
            collection_dict['id'] += "?{}".format(query_str)
            page_iri += "?{}".format(query_str)
            next_iri += "?{}".format(query_str)

        data = {
            'id': page_iri,
            'type': 'AnnotationPage',
            'partOf': collection_dict
        }

        return data

    def get(self, collection_id):
        """Get a Collection."""
        collection = self._get_collection(collection_id)
        page_links = self._get_page_links(collection)
        collection_dict = collection.dictize()
        collection_dict.update(page_links)
        return self._create_response(collection_dict)

    def post(self, collection_id):
        """Create an Annotation."""
        collection = self._get_collection(collection_id)
        return self._create(Annotation, annotation_repo, collection=collection)

    def put(self, collection_id):
        """Update a Collection."""
        collection = self._get_collection(collection_id)
        return self._update(collection, collection_repo)

    def delete(self, collection_id):
        """Delete a Collection.

        Fails if the Collection contains Annotations, or is the last one on the
        server.
        """
        collection = self._get_collection(collection_id)
        if collection_repo.count() == 1:
            msg = 'The last collection on the server so cannot be deleted'
            abort(400, msg)
        elif collection.annotations:
            msg = 'The collection is not empty so cannot be deleted'
            abort(400, msg)
        return self._delete(collection, collection_repo)
