# -*- coding: utf8 -*-
"""Repository module."""

import json
from sqlalchemy import func
from sqlalchemy.sql import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.base import _entity_descriptor
from jsonschema.exceptions import ValidationError


class Repository(object):
    """Repository class for all domain objects."""

    def __init__(self, db):
        self.db = db

    def get(self, model_cls, key):
        """Get an object by key."""
        return self.db.session.query(model_cls).get(key)

    def get_by(self, model_cls, **attrs):
        """Get an object by given attributes."""
        return self.db.session.query(model_cls).filter_by(**attrs).first()

    def filter_by(self, model_cls, **attrs):
        """Get all objects filtered by given attributes."""
        return self.db.session.query(model_cls).filter_by(**attrs).all()

    def count(self, model_cls):
        """Count all objects."""
        return self.db.session.query(model_cls).count()

    def save(self, model_cls, obj):
        """Save an object."""
        self._validate_can_be(model_cls, 'saved', obj)
        try:
            self.db.session.add(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def update(self, model_cls, obj):
        """Update an object."""
        self._validate_can_be(model_cls, 'updated', obj)
        obj.modified
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def delete(self, model_cls, key):
        """Mark an object as deleted."""
        obj = self.db.session.query(model_cls).get(key)
        self._validate_can_be(model_cls, 'deleted', obj)
        obj.deleted = True
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def batch_delete(self, model_cls, ids):
        """Mark a list of objects as deleted."""
        batch_clause = self._get_batch_clause(model_cls, ids)
        try:
            self.db.session.execute(model_cls.__table__.update()
                                                       .values(deleted=True)
                                                       .where(batch_clause))
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def _validate_batch_clause(self, model_cls, batch_clause, ids):
        """Confirm that all IDs exist for the batch clause."""
        query = model_cls.__table__.select().where(batch_clause)
        count = self.db.session.execute(query).rowcount
        if count != len(ids):
            msg = 'The query contains IDs that cannot be found in the database'
            raise ValueError(msg)

    def _get_batch_clause(self, model_cls, ids):
        """Return OR clauses for batch operations by ID."""
        clauses = []
        for _id in ids:
            clauses.append((_entity_descriptor(model_cls, 'id') == _id))
        batch_clause = or_(*clauses)
        self._validate_batch_clause(model_cls, batch_clause, ids)
        return batch_clause

    def search(self, model_cls, contains=None, fts=None, **kwargs):
        """Search for objects."""
        clauses = [_entity_descriptor(model_cls, key) == value
                   for key, value in kwargs.items() if '.' not in key]

        contains_clauses = self._get_contains_clauses(model_cls, contains)
        fts_clauses = self._get_fts_clauses(model_cls, fts)
        rel_clauses = self._get_relationship_clauses(model_cls, **kwargs)

        all_clauses = and_(
            and_(*clauses),
            and_(*contains_clauses),
            and_(*fts_clauses),
            and_(*rel_clauses)
        )
        return self.db.session.query(model_cls).filter(*all_clauses).all()

    def _get_contains_clauses(self, model_cls, query):
        """Return contains clauses."""
        clauses = []
        if query:
            try:
                q = json.loads(query)
                if isinstance(q, int) or isinstance(q, float):
                    q = '"{}"'.format(q)
            except ValueError as err:
                msg = 'Could not parse "contains": {}'.format(err.message)
                raise ValueError(msg)
            clauses.append(_entity_descriptor(model_cls, '_data').contains(q))
        return clauses

    def _get_relationship_clauses(self, model_cls, **kwargs):
        """Return relationship clauses."""
        clauses = []
        relationships = {k: v for k, v in kwargs.iteritems() if '.' in k}
        for k, v in relationships.items():
            parts = k.split('.')
            if len(parts) == 2:
                rel = parts[0]
                has = {parts[1]: v}
                clauses.append(_entity_descriptor(model_cls, rel).has(**has))
        return clauses

    def _get_fts_clauses(self, model_cls, query):
        """Return full-text search clauses."""
        clauses = []
        pairs = query.split('|') if query else []
        for pair in pairs:
            if pair != '':
                if '::' in pair:
                    k, v = pair.split("::")
                    vector = _entity_descriptor(model_cls, '_data')[k].astext
                else:
                    v = pair
                    vector = _entity_descriptor(model_cls, '_data')

                clause = func.to_tsvector(vector).match(v, postgresql_regconfig='english')
                clauses.append(clause)
        return clauses

    def _validate_can_be(self, model_cls, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, model_cls):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)
