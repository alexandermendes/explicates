# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort, request

from pywa.model.collection import Collection
from pywa.core import collection_repo, annotation_repo


blueprint = Blueprint('api', __name__)


def get_data():
    """Get request data."""
    data = request.get_json()
    data.update({
        'slug': request.headers.get('Slug')
    })
    return data


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index."""
    if request.method == 'GET':
        return 'The PYWA server'

    data = get_data()
    collection = Collection(**data)
    collection_repo.save(collection)
    return collection


@blueprint.route('/<collection_slug>')
def collection(collection_slug):
    """Return a Collection."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    return coll


@blueprint.route('/<collection_slug>/<annotation_slug>')
def annotation(collection_slug, annotation_slug):
    """Return an Annotation."""
    coll = collection_repo.get_by(slug=collection_slug)
    if not coll:
        abort(404)

    anno = annotation_repo.get_by(slug=annotation_slug, collection=coll)
    if not anno:
        abort(404)

    return anno
