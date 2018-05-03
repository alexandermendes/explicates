# -*- coding: utf8 -*-

from flask import Blueprint


blueprint = Blueprint('index', __name__)


@blueprint.route('/')
def index():
    """Render index."""
    return 'The PYWA server'
