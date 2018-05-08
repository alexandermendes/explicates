# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort, request, url_for, current_app
from jsonschema.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from pywa.model.collection import Collection
from pywa.model.annotation import Annotation
from pywa.core import collection_repo, annotation_repo


blueprint = Blueprint('api', __name__)


def handle_post(model_class, repo, **kwargs):
    """Handle POST request."""
    data = request.get_json()
    slug = request.headers.get('Slug')

    try:
        obj = model_class(data=data, slug=slug, **kwargs)
        repo.save(obj)
    except (ValidationError, IntegrityError, TypeError) as err:
        abort(400, err.message)

    return obj


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index page."""
    if request.method == 'GET':
        collections = collection_repo.get_all()
        return {
            "context": "https://www.w3.org/ns/ldp.jsonld",
            "type": "BasicContainer",
            "contains": [c.dictize() for c in collections]
        }

    return handle_post(Collection, collection_repo)


@blueprint.route('/<collection_slug>/',
                 methods=['GET', 'POST', 'PUT', 'DELETE'])
def collection(collection_slug):
    """Return a Collection."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    page = request.args.get('page', None)
    if page:
        return page_response(coll, int(page), request.query_string)

    collection_dict = coll.dictize()
    annotations = annotation_repo.filter_by(collection_key=coll.key)

    # Add items
    items = [a.dictize() for a in annotations]
    iris = request.args.get('iris', None)
    if iris:
        items = [item['id'] for item in items]
    collection_dict['items'] = items

    # Add first page
    if annotations:
        collection_dict['first'] = url_for('.collection',
                                           collection_slug=coll.slug,
                                           page=0,
                                           _external=True)
    # Add last page
    count = len(annotations)
    per_page = current_app.config.get('ANNOTATIONS_PER_PAGE')
    last_page = 0 if count <= 0 else count // per_page - 1
    if last_page:
        collection_dict['last'] = url_for('.collection',
                                          collection_slug=coll.slug,
                                          page=last_page,
                                          _external=True)

    if request.method == 'POST':
        return handle_post(Annotation, annotation_repo, collection=coll)

    return collection_dict


@blueprint.route('/<collection_slug>/<annotation_slug>',
                 methods=['GET', 'PUT', 'DELETE'])
def annotation(collection_slug, annotation_slug):
    """Return an Annotation."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    anno = annotation_repo.get_by(slug=annotation_slug, collection=coll)
    if not anno:
        abort(404)

    return anno


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

    return data
