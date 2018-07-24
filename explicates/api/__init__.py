# -*- coding: utf-8 -*-
"""API module."""

from flask.views import MethodView
from flask import Blueprint

from explicates.model.collection import Collection
from explicates.api.base import APIBase
from explicates.api.collections import CollectionsAPI
from explicates.api.annotations import AnnotationsAPI
from explicates.api.index import IndexAPI
from explicates.api.search import SearchAPI
from explicates.api.export import ExportAPI
from explicates.api.batch import BatchAPI


blueprint = Blueprint('api', __name__)


def register_api(view, endpoint, url):
    """Register API endpoints."""
    view_func = view.as_view(endpoint)
    blueprint.add_url_rule(url, view_func=view_func)


register_api(IndexAPI, 'index', '/annotations/')
register_api(CollectionsAPI, 'collections', '/annotations/<collection_id>/')
register_api(AnnotationsAPI, 'annotations',
             '/annotations/<collection_id>/<annotation_id>/')
register_api(SearchAPI, 'search', '/search/')
register_api(ExportAPI, 'export', '/export/<collection_id>/')
register_api(BatchAPI, 'batch', '/batch/')
