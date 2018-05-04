# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort

from pywa.core import collection_repo


blueprint = Blueprint('index', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index."""
    return 'The PYWA server'


@blueprint.route('/<slug>')
def collection(slug):
    """Return a collection."""
    collection = collection_repo.get_by(slug=slug)
    if not collection:
        abort(404)

    return collection
