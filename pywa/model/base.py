# -*- coding: utf8 -*-

import os
import json
import datetime
from jsonschema import validate
from jsonschema.exceptions import ValidationError


class BaseDomainObject(object):
    """Base domain object class."""

    def dictize(self):
        """Return the domain object as a dictionary."""
        out = {}
        for col in self.__table__.c:
            obj = getattr(self, col.name)
            if isinstance(obj, datetime.datetime):
                obj = obj.isoformat()
            out[col.name] = obj
        return out

    def get_json_schema(self, filename):
        """Load a JSON Schema."""
        here = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(os.path.dirname(here), 'schemas', filename)
        with open(schema_path, 'rb') as json_file:
            return json.load(json_file)

    def validate_json(self, key, obj, schema_filename):
        """Validate a JSON object."""
        schema = self.get_json_schema(schema_filename)
        try:
            validate(obj, schema)
        except ValidationError as err:
            cls_name = self.__class__.__name__
            err.message = '{0} {1} is invalid - {2}'.format(cls_name, key,
                                                            err.message)
            raise err
        return obj
