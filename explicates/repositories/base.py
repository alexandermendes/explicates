# -*- coding: utf8 -*-

from sqlalchemy.exc import IntegrityError
from jsonschema.exceptions import ValidationError


class BaseRepository(object):
    """Base repository class."""

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class

    def get(self, key):
        """Get an object by key."""
        return self.db.session.query(self.model_class).get(key)

    def get_by(self, **attributes):
        """Get an object by given attributes."""
        return self.db.session.query(self.model_class) \
                              .filter_by(**attributes) \
                              .first()

    def get_all(self):
        """Get all objects."""
        return self.db.session.query(self.model_class).all()

    def count(self):
        """Count all objects."""
        return self.db.session.query(self.model_class).count()

    def filter_by(self, **filters):
        """Get all filtered objects."""
        return self.db.session.query(self.model_class) \
                              .filter_by(**filters) \
                              .all()

    def save(self, obj):
        """Save an object."""
        self._validate_can_be('saved', obj)
        try:
            self.db.session.add(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def update(self, obj):
        """Update an object."""
        self._validate_can_be('updated', obj)
        obj.modified
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def delete(self, key):
        """Mark an object as deleted."""
        obj = self.db.session.query(self.model_class).get(key)
        self._validate_can_be('deleted', obj)
        obj.deleted = True
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except (IntegrityError, ValidationError) as err:
            self.db.session.rollback()
            raise err

    def _validate_can_be(self, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, self.model_class):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)
