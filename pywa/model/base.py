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

        # Add context
        out['@context'] = "http://www.w3.org/ns/anno.jsonld"

        # Add ID
        root_url = url_for('api.index', _external=True)
        safe_suffix = quote(self.get_id_suffix().encode('utf8'))
        out['id'] = root_url + safe_suffix

        # Add extra info
        extra = self.get_extra_info()
        out.update(extra)

        return out
