# -*- coding: utf8 -*-
"""Repository module."""

import json
from sqlalchemy import func
from sqlalchemy.sql import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.base import _entity_descriptor
from future.utils import iteritems


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
        except IntegrityError as err:  # pragma: no cover
            self.db.session.rollback()
            raise err

    def update(self, model_cls, obj):
        """Update an object."""
        self._validate_can_be(model_cls, 'updated', obj)
        obj.modified
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except IntegrityError as err:  # pragma: no cover
            self.db.session.rollback()
            raise err

    def delete(self, model_cls, key):
        """Mark an object as deleted."""
        obj = self.db.session.query(model_cls).get(key)
        obj.deleted = True
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except IntegrityError as err:  # pragma: no cover
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
        except IntegrityError as err:  # pragma: no cover
            self.db.session.rollback()
            raise err

    def _validate_batch_clause(self, model_cls, batch_clause, ids):
        """Confirm that all IDs exist for the batch clause."""
        query = model_cls.__table__.select().where(batch_clause)
        count = self.db.session.execute(query).rowcount
        if count < len(ids):
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

    def _validate_can_be(self, model_cls, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, model_cls):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)
