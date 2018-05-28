# -*- coding: utf8 -*-
"""Exporter module."""

import json
import string
import tempfile
import zipfile
import unidecode
from flask import current_app
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from explicates.core import repo, db
from explicates.model.annotation import Annotation
from explicates.model.collection import Collection


class Exporter(object):

    def _stream_annotation_data(self, collection):
        """Stream the contents of an AnnotationCollection from the database."""
        table = Annotation.__table__
        where_clauses = [
            table.c.collection_key == collection.key,
            table.c.deleted is not True
        ]

        query = table.select().where(and_(*where_clauses))
        exec_opts = dict(stream_results=True)
        res = db.session.connection(execution_options=exec_opts).execute(query)
        while True:
            chunk = res.fetchmany(10000)
            if not chunk:
                break
            for row in chunk:
                yield dict(row)

    def generate_data(self, collection_id):
        """Return all Annotations as JSON-LD."""
        collection = repo.get_by(Collection, id=collection_id)
        data_gen = self._stream_annotation_data(collection)
        first = True
        yield '['
        for row in data_gen:
            anno = Annotation(**dict(row))
            anno.collection = collection
            anno_dict = anno.dictize()
            out = json.dumps(anno_dict)
            yield out if first else ', ' + out
            first = False
        yield ']'
