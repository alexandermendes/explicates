# -*- coding: utf8 -*-
"""API module."""

from flask.views import MethodView
from flask import Blueprint

from explicates.core import collection_repo
from explicates.model.collection import Collection
from explicates.api.base import APIBase
from explicates.api.collections import CollectionsAPI
from explicates.api.annotations import AnnotationsAPI


blueprint = Blueprint('api', __name__)


def register_api(view, endpoint, url):
    """Register API endpoints."""
    view_func = view.as_view(endpoint)
    blueprint.add_url_rule(url, view_func=view_func)


register_api(CollectionsAPI, 'collections', '/annotations/<collection_id>/')
register_api(AnnotationsAPI, 'annotations',
             '/annotations/<collection_id>/<annotation_id>/')


@blueprint.route('/annotations/', methods=['POST'])
def create_collection():
    """Create a Collection."""
    api_base = APIBase()
    return api_base._create(Collection, collection_repo)
