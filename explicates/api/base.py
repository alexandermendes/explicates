# -*- coding: utf8 -*-
"""Base API module.

Design notes:

- Content Negotiation: All responses are in the JSON-LD format and use the
  Web Annotation profile, more formats may be added in future.
"""

from flask import current_app
from flask import abort, request, jsonify, make_response, url_for
from jsonschema.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from explicates.core import repo
from explicates.model.annotation import Annotation
from explicates.model.collection import Collection
from explicates.model.base import BaseDomainObject


class APIBase(object):

    def _get_domain_object(self, model_class, id, **kwargs):
        """Return a domain object."""
        obj = repo.get_by(model_class, id=id, **kwargs)
        if not obj:
            abort(404)
        elif obj.deleted:
            abort(410)
        return obj

    def _get_iri(self, obj, **kwargs):
        """Get the IRI for an existing object."""
        if isinstance(obj, Annotation):
            return url_for('api.annotations', annotation_id=obj.id,
                           collection_id=obj.collection.id, _external=True,
                           **kwargs)
        elif isinstance(obj, Collection):
            return url_for('api.collections', collection_id=obj.id,
                           _external=True, **kwargs)
        cls_name = obj.__class__.__name__
        raise TypeError('Cannot generated IRI for {}'.format(cls_name))

    def _create(self, model_class, **kwargs):
        """Create and return a domain object."""
        data = request.get_json()
        slug = request.headers.get('Slug')
        try:
            obj = model_class(id=slug, data=data, **kwargs)
            repo.save(model_class, obj)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)
        return obj

    def _update(self, obj):
        """Update a domain object."""
        data = request.get_json()
        try:
            obj.data = data
            model_class = obj.__class__
            repo.update(model_class, obj)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)

    def _delete(self, obj):
        """Delete a domain object."""
        try:
            model_class = obj.__class__
            repo.delete(model_class, obj.key)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)

    def _create_response(self, rv, status_code=200, headers=None):
        """Return a JSON-LD Response.

        The Web Annotation profile is used for Web Annotations.

        See https://www.w3.org/TR/annotation-protocol/#annotation-retrieval
        """
        out = rv if rv else {}
        if isinstance(rv, BaseDomainObject):
            out = rv.dictize()

        if not isinstance(out, dict):
            err_msg = '{} is not a valid return value'.format(type(rv))
            raise TypeError(err_msg)

        # Set context and content-type
        mimetype = 'application/ld+json'
        types = out.get('type', [])
        if isinstance(types, basestring):
            types = [types]
        anno_types = ['Annotation', 'AnnotationCollection', 'AnnotationPage']
        if set(anno_types).intersection(set(types)):
            out['@context'] = "http://www.w3.org/ns/anno.jsonld"
            profile = 'profile="http://www.w3.org/ns/anno.jsonld"'
            mimetype += '; {}'.format(profile)
        response = jsonify(out)
        response.mimetype = mimetype

        # Add Etags for HEAD and GET requests
        if request.method in ['HEAD', 'GET']:
            response.add_etag()

        # Add headers
        self._add_link_headers(response, out)
        common_headers = getattr(self, 'headers', {})
        response.headers.extend(common_headers)
        if headers:
            response.headers.extend(headers)

        response.status_code = status_code
        return response

    def _add_link_headers(self, response, out):
        """Add Link headers basic on the domain object."""
        types = out.get('type', [])
        if isinstance(types, basestring):
            types = [types]

        urls = []
        if 'Annotation' in types:
            urls.append('http://www.w3.org/ns/ldp#Resource')
        if 'AnnotationCollection' in types:
            urls.append('http://www.w3.org/ns/oa#AnnotationCollection')
        if 'AnnotationPage' in types:
            urls.append('http://www.w3.org/ns/oa#AnnotationPage')
        if 'BasicContainer' in types:
            urls.append('http://www.w3.org/ns/ldp#BasicContainer')
        if 'DirectContainer' in types:
            urls.append('http://www.w3.org/ns/ldp#DirectContainer')
        if 'IndirectContainer' in types:
            urls.append('http://www.w3.org/ns/ldp#IndirectContainer')

        links = [dict(url=url, rel='type') for url in urls]
        containers = ['BasicContainer', 'DirectContainer', 'IndirectContainer']
        if set(containers).intersection(set(types)):
            links.append({
                'url': 'http://www.w3.org/TR/annotation-protocol/',
                'rel': 'http://www.w3.org/ns/ldp#constrainedBy'
            })

        for link in links:
            link_str = '<{0}>; rel="{1}"'.format(link['url'], link['rel'])
            response.headers.add('Link', link_str)

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

    def _get_container(self, collection):
        """Return the Collection with the requested representation.

        https://www.w3.org/TR/annotation-protocol/#container-representations
        """
        out = collection.dictize()
        minimal, iris = self._get_container_preferences()
        params = self._get_query_params()
        params['iris'] = 1 if iris or params.get('iris') == '1' else None

        out['id'] = self._get_iri(collection, **params)

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
            return self._get_iri(collection, page=0, **params)

    def _get_last_page_iri(self, collection, **params):
        """Return the IRI for the last AnnotationPage in a Collection."""
        last_page = self._get_last_page(collection)
        if last_page > 0:
            return self._get_iri(collection, page=last_page, **params)

    def _get_page(self, page, collection, partof=None, **params):
        """Return an AnnotationPage."""
        page_iri = self._get_iri(collection, page=page, **params)
        data = {
            'type': 'AnnotationPage',
            'id': page_iri,
            'startIndex': 0
        }

        last_page = self._get_last_page(collection)
        if last_page > page:
            data['next'] = self._get_iri(collection, page=page + 1, **params)

        if partof:
            data['partOf'] = partof

        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        annotations = collection.annotations[page:page + per_page]
        items = []
        for annotation in annotations:
            anno_params = params.copy()
            anno_params.pop('iris', None)
            anno_dict = annotation.dictize()
            anno_dict['id'] = self._get_iri(annotation, **anno_params)
            if params.get('iris'):
                items.append(anno_dict['id'])
            else:
                items.append(anno_dict)

        data['items'] = items
        return data
