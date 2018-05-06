# -*- coding: utf8 -*-

import os
import json
import datetime
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from flask import current_app, url_for

from pywa.model import make_timestamp

try:
    from urllib import quote
except ImportError:  # py3
    from urllib.parse import quote


class BaseDomainObject(object):
    """Base domain object class."""

    def dictize(self):
        """Return the domain object as a dictionary."""
        filtered = ['key', 'slug', 'collection_key']
        out = {}
        for col in self.__table__.c:
            obj = getattr(self, col.name)
            if not obj or col.name in filtered:
                continue
            out[col.name] = obj

        # Add ID
        root_url = url_for('api.index', _external=True)
        safe_suffix = quote(self.get_id_suffix().encode('utf8'))
        out['id'] = root_url + safe_suffix

        # Add extra info
        extra = self.get_extra_info()
        out.update(extra)

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
