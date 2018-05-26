# -*- coding: utf8 -*-
"""Search module."""

import json
from sqlalchemy import func
from sqlalchemy.sql import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.base import _entity_descriptor
from future.utils import iteritems
try:
    from urllib.parse import unquote
    from json.decoder import JSONDecodeError
except ImportError:  # py2
    from urllib import unquote
    JSONDecodeError = ValueError

from explicates.model.collection import Collection
from explicates.model.annotation import Annotation



class Search(object):
    """Search class for Annotations."""

    def __init__(self, db):
        self.db = db

    def search(self, contains=None, collection=None, limit=None,
               range=None, order_by='created'):
        """Search for Annotations."""
        clauses = []
        if contains:
            contains_clause = self._get_contains_clause(contains)
            clauses.append(contains_clause)

        if collection:
            collection_clause = self._get_collection_clause(collection)
            clauses.append(collection_clause)

        if range:
            range_clauses = self._get_range_clauses(range)
            clauses.append(and_(*range_clauses))

        joined_clauses = and_(*clauses)
        return (self.db.session.query(Annotation)
                .join(Collection)
                .filter(*clauses)
                .order_by(order_by)
                .limit(limit)
                .all())

    def _parse_json(self, key, data):
        if isinstance(data, dict):
            return data
        try:
            q = json.loads(data)
            if isinstance(q, int) or isinstance(q, float):
                q = '"{}"'.format(q)
        except JSONDecodeError as err:
            msg = 'invalid "{0}" clause: {1}'.format(key, str(err))
            raise ValueError(msg)
        return q

    def _get_contains_clause(self, data):
        """Return contains clause."""
        query = self._parse_json('contains', data)
        return Annotation._data.contains(query)

    def _get_collection_clause(self, iri):
        """Return Collection by IRI."""
        collection_id = unquote(iri).rstrip('/').split('/')[-1]
        return (Collection.id == collection_id)

    def _get_range_clauses(self, data):
        """Return range clauses."""
        query = self._parse_json('range', data)
        err_base = 'invalid "range" clause'
        clauses = []
        for col, operators in query.items():
            desc = _entity_descriptor(Annotation, col)
            if not isinstance(operators, dict):
                msg = '{0}: {1} is not {2}'.format(err_base, col, dict)
                raise ValueError(msg)
            for op, value in operators.items():
                if op == 'lte':
                    clauses.append(desc <= value)
                    continue
                elif op == 'lt':
                    clauses.append(desc < value)
                    continue
                elif op == 'gte':
                    clauses.append(desc >= value)
                    continue
                elif op == 'gt':
                    clauses.append(desc > value)
                    continue
                msg = '{0}: {1} is not a known operator'.format(err_base, op)
                raise ValueError(msg)
        return clauses

    # def _get_fts_clauses(self, model_cls, query):
    #     """Return full-text search clauses."""
    #     clauses = []
    #     pairs = query.split('|') if query else []
    #     for pair in pairs:
    #         if pair != '':
    #             if '::' in pair:
    #                 k, v = pair.split("::")
    #                 vector = _entity_descriptor(model_cls, '_data')[k].astext
    #             else:
    #                 v = pair
    #                 vector = _entity_descriptor(model_cls, '_data')

    #             clause = func.to_tsvector(vector).match(v, postgresql_regconfig='english')
    #             clauses.append(clause)
    #     return clauses