# -*- coding: utf8 -*-


class Repository(object):

    def __init__(self, db):
        self.db = db

    def get(self, id):
        return self.db.session.query(self.__class__).get(id)

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
        result = self.db.session.query(self.__class__).filter(self.__class__.id==obj.id).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def _validate_can_be(self, action, obj):
        """Verify that the query is for an object of the right type."""
        if not isinstance(obj, self.__class__):
            name = obj.__class__.__name__
            msg = '{0} cannot be {1} by {2}'.format(name,
                                                    action,
                                                    self.__class__.__name__)
            raise ValueError(msg)


from annotation import AnnotationRepository
from collection import CollectionRepository


assert AnnotationRepository
assert CollectionRepository
