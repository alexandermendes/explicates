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

    if request.method == 'POST':
        return handle_post(Annotation, annotation_repo, collection=coll)

    return coll


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
