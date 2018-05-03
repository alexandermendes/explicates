# -*- coding: utf8 -*-

import uuid
import datetime


def make_timestamp(self):
    """Return timestamp expressed in the UTC xsd:datetime format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def make_uuid(self):
    """Return a UUID."""
    return str(uuid.uuid4())