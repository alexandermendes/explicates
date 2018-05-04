# -*- coding: utf8 -*-

from sqlalchemy.exc import IntegrityError


class Repository(object):

    def __init__(self, db, model_class):
        self.db = db
        self.model_class = model_class

    def get(self, id):
        return self.db.session.query(self.model_class).get(id)

    def get_by(self, **attributes):
        return self.db.session.query(self.model_class).filter_by(**attributes).first()

    def save(self, obj):
        """Save an object."""
        self._validate_can_be('saved', obj)
        try:
            self.db.session.add(obj)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise IntegrityError

    def update(self, obj):
        """Update an object."""
        self._validate_can_be('updated', obj)
        try:
            self.db.session.merge(obj)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise IntegrityError

    def delete(self, obj):
        self._validate_can_be('deleted', obj)
        result = self.db.session.query(self.__class__).filter(self.model_class.id==obj.id).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def _validate_can_be(self, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, self.model_class):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)


from annotation import AnnotationRepository
from collection import CollectionRepository


assert AnnotationRepository
assert CollectionRepository
