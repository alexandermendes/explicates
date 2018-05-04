# -*- coding: utf8 -*-

import json
from flask import Blueprint, abort

from pywa.core import collection_repo


blueprint = Blueprint('api', __name__)


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """Render index."""
    return 'The PYWA server'


@blueprint.route('/<slug>')
def collection(slug):
    """Return a collection."""
    coll = collection_repo.get_by(slug=slug)
    if not coll:
        abort(404)

    return coll
