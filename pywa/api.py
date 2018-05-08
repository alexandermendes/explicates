# -*- coding: utf8 -*-

import json
from rdflib import *
from flask import Blueprint, abort, request, url_for, current_app
from flask import make_response
from jsonschema.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from pywa.model.collection import Collection
from pywa.model.annotation import Annotation
from pywa.core import collection_repo, annotation_repo

try:
    from urllib import urlencode
except ImportError:  # py3
    from urllib.parse import urlencode


blueprint = Blueprint('api', __name__)


def respond(data, status_code=200):
    """Return a response.

    See https://www.w3.org/TR/annotation-protocol/#annotation-retrieval
    """
    accepted_types = [
        'application/ld+json',
        'text/turtle'
    ]
    best = request.accept_mimetypes.best_match(accepted_types,
                                               default='application/ld+json')

    # Content negotiation
    if best == 'text/turtle':
        try:
            data = convert_json_ld(json.dumps(data), 'turtle')
        except Exception as err:
            abort(406, err)
        response = make_response(data)
        response.mimetype = 'text/turtle'
    else:
        response = make_response(data)
        profile = '"http://www.w3.org/ns/anno.jsonld"'
        response.mimetype = 'application/ld+json; profile={0}'.format(profile)

    # Add Link headers
    link = '<http://www.w3.org/ns/ldp#Resource>; rel="type"'
    response.headers['Link'] = link

    # Add Vary header for HEAD and GET requests
    if request.method in ['HEAD', 'GET']:
        response.headers['Vary'] = 'Accept'
        response.add_etag()

    # Add Location of newly created objects
    elif request.method == 'POST' and data and 'id' in data:
        response.headers['Location'] = data['id']

    response.status_code = status_code
    return response


def convert_json_ld(json, out_format):
    """Convert JSON-LD to an alternative representation."""
    g = ConjunctiveGraph()
    g.parse(data=json, format="json-ld")
    return g.serialize(format=out_format)


def handle_post(model_class, repo, **kwargs):
    """Handle POST request."""
    data = request.get_json()
    slug = request.headers.get('Slug')

    try:
        obj = model_class(data=data, slug=slug, **kwargs)
        repo.save(obj)
    except (ValidationError, IntegrityError, TypeError) as err:
        abort(400, err.message)

    return respond(obj.dictize(), status_code=201)


def handle_put(obj, repo):
    """Handle PUT request."""
    data = request.get_json()
    try:
        obj.data = data
        repo.update(obj)
    except (ValidationError, IntegrityError, TypeError) as err:
        abort(400, err.message)

    return respond(obj.dictize(), status_code=200)


def handle_delete(obj, repo):
    """Handle DELETE request."""
    try:
        repo.delete(obj.key)
    except (ValidationError, IntegrityError, TypeError) as err:
        abort(400, err.message)

    return respond({}, status_code=204)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index page."""
    if request.method == 'GET':
        collections = collection_repo.get_all()
        data = {
            "context": "https://www.w3.org/ns/ldp.jsonld",
            "type": "BasicContainer",
            "contains": [c.dictize() for c in collections]
        }
        return respond(data)

    return handle_post(Collection, collection_repo)


@blueprint.route('/<collection_slug>/',
                 methods=['GET', 'POST', 'PUT', 'DELETE'])
def collection(collection_slug):
    """Collection endpoint."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)
    elif coll.deleted:
        abort(410)

    page = request.args.get('page', None)
    if page:
        return page_response(coll, int(page), request.query_string)

    collection_dict = coll.dictize()
    annotations = annotation_repo.filter_by(collection_key=coll.key)

    kwargs = get_valid_request_args()
    if kwargs:
        query_str = urlencode(kwargs)
        collection_dict['id'] += "?{}".format(query_str)

    # Add first page
    if annotations:
        collection_dict['first'] = url_for('.collection',
                                           collection_slug=coll.slug,
                                           page=0,
                                           _external=True,
                                           **kwargs)
    # Add last page
    count = len(annotations)
    per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
    last_page = 0 if count <= 0 else count // per_page - 1
    if last_page:
        collection_dict['last'] = url_for('.collection',
                                          collection_slug=coll.slug,
                                          page=last_page,
                                          _external=True,
                                          **kwargs)

    if request.method == 'POST':
        return handle_post(Annotation, annotation_repo, collection=coll)

    elif request.method == 'PUT':
        return handle_put(coll, collection_repo)

    elif request.method == 'DELETE':
        count = collection_repo.count()
        if count <= 1:
            # The server must retain at least one container
            # https://www.w3.org/TR/annotation-protocol/#annotation-containers
            msg = 'This is the last collection on the server so cannot ', \
                  'be deleted'
            abort(400, msg)
        elif annotations:
            msg = 'The collection is not empty so cannot be deleted'
            abort(400, msg)
        else:
            return handle_delete(coll, collection_repo)

    return respond(collection_dict)


@blueprint.route('/<collection_slug>/<annotation_slug>/',
                 methods=['GET', 'PUT', 'DELETE'])
def annotation(collection_slug, annotation_slug):
    """Return an Annotation."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    anno = annotation_repo.get_by(slug=annotation_slug, collection=coll)
    if not anno:
        abort(404)
    elif anno.deleted:
        abort(410)

    if request.method == 'DELETE':
        return handle_delete(anno, annotation_repo)
    elif request.method == 'PUT':
        return handle_put(anno, annotation_repo)

    return respond(anno.dictize())


def page_response(collection, page, query_str):
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

    return respond(data)


def get_valid_request_args():
    """Return valid request args to be appended to IRIs."""
    kwargs = {
        'iris': request.args.get('iris', None)
    }
    return dict((k,v) for k,v in kwargs.iteritems() if v is not None)
