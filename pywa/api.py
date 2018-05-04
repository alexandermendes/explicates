# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort

from pywa.core import collection_repo, annotation_repo


blueprint = Blueprint('api', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index."""
    return 'The PYWA server'


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
