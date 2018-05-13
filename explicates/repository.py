# -*- coding: utf8 -*-
"""Repository module."""

from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError


class Repository(object):
    """Repository class for all domain objects."""

    def __init__(self, db):
        self.db = db

    def get(self, model_class, key):
        """Get an object by key."""
        return self.db.session.query(model_class).get(key)

    def get_by(self, model_class, **attrs):
        """Get an object by given attributes."""
        return self.db.session.query(model_class).filter_by(**attrs).first()

    def count(self, model_class):
        """Count all objects."""
        return self.db.session.query(model_class).count()

    def save(self, model_class, obj):
        """Save an object."""
        self._validate_can_be(model_class, 'saved', obj)
        try:
            self.db.session.add(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def update(self, model_class, obj):
        """Update an object."""
        self._validate_can_be(model_class, 'updated', obj)
        obj.modified
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def delete(self, model_class, key):
        """Mark an object as deleted."""
        obj = self.db.session.query(model_class).get(key)
        self._validate_can_be(model_class, 'deleted', obj)
        obj.deleted = True
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def _validate_can_be(self, model_class, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, model_class):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)
