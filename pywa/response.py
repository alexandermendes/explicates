# -*- coding: utf8 -*-

from flask import request


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
    response.headers['Allow'] = 'GET,OPTIONS,HEAD'

    if request.method in ['HEAD', 'GET']:
        response.headers['Vary'] = 'Accept'
        response.add_etag()

    return response
