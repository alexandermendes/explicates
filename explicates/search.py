# -*- coding: utf-8 -*-
"""Search module."""

import json
from sqlalchemy import func
from sqlalchemy.sql import and_, or_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.base import _entity_descriptor
from future.utils import iteritems

try:  # pragma: no cover
    from urllib.parse import unquote
except ImportError:  # pragma: no cover
    from urllib import unquote

try:  # pragma: no cover
    from json.decoder import JSONDecodeError
except ImportError:  # pragma: no cover
    JSONDecodeError = ValueError

from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


class Search(object):
    """Search class for Annotations."""

    def __init__(self, db):
        self.db = db

    def search(self, contains=None, collection=None, fts=None, fts_phrase=None,
               limit=None, range=None, order_by='created', offset=0):
        """Search for Annotations."""
        clauses = []
        if contains:
            contains_clause = self._get_contains_clause(contains)
            clauses.append(contains_clause)

        if collection:
            collection_clause = self._get_collection_clause(collection)
            clauses.append(collection_clause)

        if fts:
            fts_clauses = self._get_fts_clauses(fts)
            clauses.append(and_(*fts_clauses))

        if fts_phrase:
            fts_phrase_clauses = self._get_fts_phrase_clauses(fts_phrase)
            clauses.append(and_(*fts_phrase_clauses))

        if range:
            range_clauses = self._get_range_clauses(range)
            clauses.append(and_(*range_clauses))

        if len(clauses) > 1:
            clauses = and_(*clauses)

        return (self.db.session.query(Annotation)
                .join(Collection)
                .filter(*clauses)
                .order_by(order_by)
                .limit(limit)
                .offset(offset)
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
        q = self._parse_json('range', data)
        err_base = 'invalid "range" clause'
        clauses = []
        for col, operators in q.items():
            vector = self._get_vector(col)
            if not isinstance(operators, dict):
                msg = '{0}: {1} is not {2}'.format(err_base, col, dict)
                raise ValueError(msg)
            for op, value in operators.items():
                if op == 'lte':
                    clauses.append(vector <= str(value))
                    continue
                elif op == 'lt':
                    clauses.append(vector < str(value))
                    continue
                elif op == 'gte':
                    clauses.append(vector >= str(value))
                    continue
                elif op == 'gt':
                    clauses.append(vector > str(value))
                    continue
                msg = '{0}: {1} is not a known operator'.format(err_base, op)
                raise ValueError(msg)
        return clauses

    def _get_fts_clauses(self, data):
        """Return full-text search clauses."""
        q = self._parse_json('fts', data)
        err_base = 'invalid "fts" clause'
        clauses = []
        for col, settings in q.items():
            vector = self._get_vector(col)

            # Check params
            if not isinstance(settings, dict):
                msg = '{0}: {1} is not {2}'.format(err_base, col, dict)
                raise ValueError(msg)
            query = settings.get('query')
            if not query:
                msg = '{0}: "query" is required'.format(err_base)
                raise ValueError(msg)
            operator = settings.get('operator', 'and')
            prefix = settings.get('prefix', True)

            # Generate clauses
            tokens = query.split()
            word_clauses = []
            for t in tokens:
                if prefix:
                    t += ':*'
                clause = func.to_tsvector(vector).match(t)
                word_clauses.append(clause)
            if operator == 'or':
                clauses.append(or_(*word_clauses))
            else:
                clauses.append(and_(*word_clauses))

            return clauses

    def _get_fts_phrase_clauses(self, data):
        """Return full-text search phrase clauses."""
        q = self._parse_json('fts_phrase', data)
        err_base = 'invalid "fts_phrase" clause'
        clauses = []
        for col, settings in q.items():
            vector = self._get_vector(col)

            # Check params
            if not isinstance(settings, dict):
                msg = '{0}: {1} is not {2}'.format(err_base, col, dict)
                raise ValueError(msg)
            query = settings.get('query')
            if not query:
                msg = '{0}: "query" is required'.format(err_base)
                raise ValueError(msg)
            distance = settings.get('distance', 1)
            operator = ' <{}> '.format(distance)

            # Generate clause
            tokens = query.split()
            word_clauses = []
            query_str = operator.join(tokens)
            ts_query = func.to_tsquery(query_str)
            clause = func.to_tsvector(vector).op('@@')(ts_query)
            clauses.append(clause)

        return clauses

    def _get_vector(self, col):
        """Return the query vector."""
        try:
            return _entity_descriptor(Annotation, col)
        except InvalidRequestError:
            return _entity_descriptor(Annotation, '_data')[col]
