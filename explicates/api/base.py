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

    def _get_domain_object(self, model_cls, id, **kwargs):
        """Return a domain object."""
        obj = repo.get_by(model_cls, id=id, **kwargs)
        if not obj:
            abort(404)
        elif obj.deleted:
            abort(410)
        return obj

    def _get_iri(self, obj, **kwargs):
        """Get the IRI for an object."""

        if isinstance(obj, Annotation):
            kwargs.pop('iris', None)
            return url_for('api.annotations', annotation_id=obj.id,
                           collection_id=obj.collection.id, _external=True,
                           **kwargs)

        elif isinstance(obj, Collection):
            if not obj.id:
                return url_for('api.search', _external=True, **kwargs)
            return url_for('api.collections', collection_id=obj.id,
                           _external=True, **kwargs)

        cls_name = obj.__class__.__name__
        raise TypeError('Cannot generated IRI for {}'.format(cls_name))

    def _create(self, model_cls, **kwargs):
        """Create and return a domain object."""
        data = request.get_json()
        slug = request.headers.get('Slug')
        try:
            obj = model_cls(id=slug, data=data, **kwargs)
            repo.save(model_cls, obj)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)
        return obj

    def _update(self, obj):
        """Update a domain object."""
        data = request.get_json()
        try:
            obj.data = data
            model_cls = obj.__class__
            repo.update(model_cls, obj)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)

    def _delete(self, obj):
        """Delete a domain object."""
        try:
            model_cls = obj.__class__
            repo.delete(model_cls, obj.key)
        except (ValidationError, IntegrityError, TypeError) as err:
            abort(400, err.message)

    def _jsonld_response(self, rv, status_code=200, headers=None):
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

        context = 'http://www.w3.org/ns/anno.jsonld'
        out['@context'] = context
        response = jsonify(out)
        response.mimetype = 'application/ld+json; profile="{}"'.format(context)

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

        namespaces = []
        if 'Annotation' in types:
            namespaces.append('ldp#Resource')
        if 'AnnotationCollection' in types:
            namespaces.append('oa#AnnotationCollection')
        if 'AnnotationPage' in types:
            namespaces.append('oa#AnnotationPage')
        if 'BasicContainer' in types:
            namespaces.append('ldp#BasicContainer')
        if 'DirectContainer' in types:
            namespaces.append('ldp#DirectContainer')
        if 'IndirectContainer' in types:
            namespaces.append('ldp#IndirectContainer')

        links = [dict(url='http://www.w3.org/ns/{}'.format(ns), rel='type')
                      for ns in namespaces]
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

        Remove page as this will be dealt with seperately.
        """
        params = request.args.copy()
        params.pop('page', None)
        return params.to_dict(flat=True)

    def _get_container(self, obj, items=None, total=None):
        """Return a container for Annotations."""
        out = obj.dictize()
        minimal, iris = self._get_container_preferences()
        params = self._get_query_params()
        params['iris'] = 1 if iris or params.get('iris') == '1' else None

        out['id'] = self._get_iri(obj, **params)

        if total:
            out['total'] = total

        page = request.args.get('page')
        if page:
            return self._get_page(int(page), obj, items, partof=out, **params)

        if items:
            if minimal:
                out['first'] = self._get_iri(obj, page=0, **params)
            else:
                out['first'] = self._get_page(0, obj, items, **params)

            last_page = self._get_last_page(items)
            if last_page > 0:
                out['last'] = self._get_iri(obj, page=last_page, **params)

        return out

    def _get_last_page(self, items):
        """Get the last page number (zero-based)."""
        total = len(items)
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        last_page = 0 if total <= 0 else (total - 1) // per_page
        return last_page

    def _get_page(self, page, obj, items, partof=None, **params):
        """Return an AnnotationPage."""
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        start = page * per_page if page > 0 else 0
        page_items = items[start:start + per_page]
        if not page_items:
            abort(404)

        page_iri = self._get_iri(obj, page=page, **params)
        data = {
            'id': page_iri,
            'type': 'AnnotationPage',
            'startIndex': 0
        }

        last_page = self._get_last_page(items)
        if last_page > page:
            data['next'] = self._get_iri(obj, page=page + 1, **params)
        if page > 0:
            data['prev'] = self._get_iri(obj, page=page - 1, **params)

        if partof:
            data['partOf'] = partof

        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
        items = self._decorate_page_items(page_items, params.get('iris'))
        data['items'] = items
        return data

    def _decorate_page_items(self, page_items, iris=False):
        """Dictize and decorate a list of page items."""
        out = []
        for page_item in page_items:
            item_dict = page_item.dictize()
            item_dict['id'] = self._get_iri(page_item)
            if iris:
                out.append(item_dict['id'])
            else:
                out.append(item_dict)
        return out
