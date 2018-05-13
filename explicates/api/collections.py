# -*- coding: utf8 -*-
"""Collections API module."""

import json
from flask import url_for, current_app, request, abort
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

    def _get_container_preferences(self):
        """Get container preferences.

        Defaults to PreferContainedDescriptions.
        """
        minimal = False
        iris = False
        prefer = request.headers.get('Prefer')
        if not prefer:
            return minimal, iris
        try:
            _return, include = prefer.split(';')
        except ValueError:
            return minimal, iris
        if _return.strip() != 'return=representation':
            return minimal, iris
        if not include.strip().startswith('include='):
            return minimal, iris
        parts = include.split('=')[1].split()
        prefs = [part.strip('"') for part in parts]

        if 'http://www.w3.org/ns/ldp#PreferMinimalContainer' in prefs:
            minimal = True
        if 'http://www.w3.org/ns/oa#PreferContainedIRIs' in prefs:
            iris = True

        return minimal, iris

    def _get_query_params(self, iris=None):
        """Return a copy of the request arguments.

        Remove page as this will be dealt with seperately for each IRI.
        """
        params = request.args.copy()
        params.pop('page', None)
        return params.to_dict(flat=True)

    def _get_container_representation(self, collection):
        """Return the Collection with the requested representation.

        https://www.w3.org/TR/annotation-protocol/#container-representations
        """

        out = collection.dictize()
        minimal, iris = self._get_container_preferences()
        params = self._get_query_params()
        params['iris'] = 1 if iris or params.get('iris') == '1' else None

        out['id'] = self._get_iri('api.collections',
                                  collection_id=collection.id, **params)

        page = request.args.get('page')
        if page:
            return self._get_page(int(page), collection, partof=out, **params)

        if collection.annotations:
            if minimal:
                out['first'] = self._get_first_page_iri(collection, **params)
            else:
                out['first'] = self._get_page(0, collection, **params)

            last = self._get_last_page_iri(collection, **params)
            if last:
                out['last'] = last

        return out

    def _get_last_page(self, collection):
        """Get the last page number for a Collection.

        Pagination is zero-based.
        """
        count = len(collection.annotations)
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = 0 if count <= 0 else (count - 1) // per_page
        return last_page

    def _get_first_page_iri(self, collection, **params):
        """Return the IRI for the first AnnotationPage in a Collection."""
        if collection.annotations:
            return self._get_iri('api.collections', page=0,
                                 collection_id=collection.id, **params)

    def _get_last_page_iri(self, collection, **params):
        """Return the IRI for the last AnnotationPage in a Collection."""
        last_page = self._get_last_page(collection)
        if last_page > 0:
            return self._get_iri('api.collections', page=last_page,
                                 collection_id=collection.id, **params)

    def _get_page(self, page, collection, partof=None, **params):
        """Return an AnnotationPage."""
        page_iri = self._get_iri('api.collections', page=page,
                                 collection_id=collection.id, **params)
        data = {
            'type': 'AnnotationPage',
            'id': page_iri,
            'startIndex': 0
        }

        last_page = self._get_last_page(collection)
        if last_page > page:
            data['next'] = self._get_iri('api.collections', page=page + 1,
                                         collection_id=collection.id,
                                         **params)

        if partof:
            data['partOf'] = partof

        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        annotations = collection.annotations[page:page + per_page]
        items = []
        for annotation in annotations:
            anno_params = params.copy()
            anno_params.pop('iris', None)
            anno_dict = annotation.dictize()
            anno_dict['id'] = self._get_iri('api.annotations',
                                            collection_id=collection.id,
                                            annotation_id=annotation.id,
                                            **anno_params)
            if params.get('iris'):
                items.append(anno_dict['id'])
            else:
                items.append(anno_dict)

        data['items'] = items
        return data

    def get(self, collection_id):
        """Get a Collection."""
        collection = self._get_collection(collection_id)
        container = self._get_container_representation(collection)
        return self._create_response(container)

    def post(self, collection_id):
        """Create an Annotation."""
        collection = self._get_collection(collection_id)
        annotation = self._create(Annotation, collection=collection)
        extra_headers = {'Location': annotation.iri}
        return self._create_response(annotation, status_code=201,
                                     headers=extra_headers)

    def put(self, collection_id):
        """Update a Collection."""
        collection = self._get_collection(collection_id)
        self._update(collection)
        container = self._get_container_representation(collection)
        return self._create_response(container)

    def delete(self, collection_id):
        """Delete a Collection.

        Fails if the Collection contains Annotations, or is the last one on the
        server.
        """
        collection = self._get_collection(collection_id)
        if repo.count(Collection) == 1:
            msg = 'The last collection on the server so cannot be deleted'
            abort(400, msg)
        elif collection.annotations:
            msg = 'The collection is not empty so cannot be deleted'
            abort(400, msg)
        self._delete(collection)
        return self._create_response(None, status_code=204)
