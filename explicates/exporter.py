# -*- coding: utf8 -*-
"""Exporter module."""

import json
import string
import tempfile
import zipfile
import pandas
import unidecode
import flatten_json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from explicates.core import repo, db
from explicates.model.annotation import Annotation
from explicates.model.collection import Collection


class Exporter(object):

    def _stream_annotation_data(self, collection_id):
        """Stream the contents of an AnnotationCollection from the database."""
        collection = repo.get_by(Collection, id=collection_id)
        table = Annotation.__table__
        query = table.select().where(table.c.collection_key == collection.key)
        exec_opts = dict(stream_results=True)
        res = db.session.connection(execution_options=exec_opts).execute(query)
        while True:
            chunk = res.fetchmany(10000)
            if not chunk:
                break
            for row in chunk:
                yield dict(row)

    def generate_data(self, collection_id, flatten=False):
        """Return all Annotations as JSON-LD."""
        data_gen = self._stream_annotation_data(collection_id)
        first = True
        yield '['
        for row in data_gen:
            if flatten:
                row = flatten_json.flatten(row)
            out = json.dumps(row)
            yield out if first else ', ' + out
            first = False
        yield ']'
