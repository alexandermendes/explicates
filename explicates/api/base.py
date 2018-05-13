# -*- coding: utf8 -*-
"""Base API module.

Design notes:

- Content Negotiation: All responses are in the JSON-LD format and use the
  Web Annotation profile, more formats may be added in future.
"""

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

    def _get_iri(self, endpoint, **kwargs):
        """Get the IRI for an existing domain object."""
        return url_for(endpoint, _external=True, **kwargs)

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
        """Return a Response.

        Currently, the server only supports the JSON-LD representation using
        the Web Annotation profile.

        See https://www.w3.org/TR/annotation-protocol/#annotation-retrieval
        """


        out = rv if rv else {}
        if isinstance(rv, BaseDomainObject):
            out = rv.dictize()

        if not isinstance(out, dict):
            err_msg = '{} is not a valid return value'.format(type(rv))
            raise TypeError(err_msg)

        out['@context'] = "http://www.w3.org/ns/anno.jsonld"

        response = jsonify(out)

        profile = '"http://www.w3.org/ns/anno.jsonld"'
        response.mimetype = 'application/ld+json; profile={0}'.format(profile)

        # Add Etags for HEAD and GET requests
        if request.method in ['HEAD', 'GET']:
            response.add_etag()

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
