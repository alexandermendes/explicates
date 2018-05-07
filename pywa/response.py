# -*- coding: utf8 -*-

from flask import request, jsonify, Response

from pywa.model.base import BaseDomainObject


class ContextualResponse(Response):

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, BaseDomainObject):
            rv = rv.dictize()
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(ContextualResponse, cls).force_type(rv, environ)


def process_response(response):
    """Modify the response object before it's sent to the server.

    Returns a JSON-LD representation using the Web Annotation profile by
    default.

    See https://www.w3.org/TR/annotation-protocol/#annotation-retrieval
    """
    profile = '"http://www.w3.org/ns/anno.jsonld"'
    response.mimetype = 'application/ld+json; profile={0}'.format(profile)
    link = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'
    response.headers['Link'] = link

    data = response.get_json(silent=True)

    if request.method in ['HEAD', 'GET']:
        response.headers['Vary'] = 'Accept'
        response.add_etag()

    elif request.method == 'POST' and data and 'id' in data:
        response.headers['Location'] = data['id']

    return response
