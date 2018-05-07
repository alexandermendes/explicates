# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort, request

from pywa.model.collection import Collection
from pywa.model.annotation import Annotation
from pywa.core import collection_repo, annotation_repo


blueprint = Blueprint('api', __name__)


def handle_post(model_class, repo, **kwargs):
    """Handle POST request."""
    data = request.get_json()
    data.update({
        'slug': request.headers.get('Slug')
    })
    data.update(kwargs)
    obj = model_class(**data)
    repo.save(obj)
    return obj


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index."""
    if request.method == 'GET':
        return 'The PYWA server'

    return handle_post(Collection, collection_repo)


@blueprint.route('/<collection_slug>',
                 methods=['GET', 'POST', 'PUT', 'DELETE'])
def collection(collection_slug):
    """Return a Collection."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    page = request.args.get('page', None)
    if page:
        return respond_page(collection, int(page))

    collection_dict = coll.dictize()
    annotations = annotation_repo.filter_by(collection_key=coll.key)
    if annotations:
        collection_dict['first'] = url_for('')

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


def page_response(collection, page):
    """Respond with a Page of a Collection."""
    collection_dict = collection.dictize()
    page_iri = "{0}/{1}".format(collection_dict['id'], page)
    next_uri = "{0}/{1}".format(collection_dict['id'], page + 1)

    if query_str:
        collection_dict['id'] += "?{}".format(query_str)
        page_iri += "?{}".format(query_str)
        next_iri += "?{}".format(query_str)

    data = {
        'id': page_iri,
        'type': 'AnnotationPage',
        'partOf': collection_dict
    }