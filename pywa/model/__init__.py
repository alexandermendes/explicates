# -*- coding: utf8 -*-

import datetime


def make_timestamp(self):
    """Return timestamp expressed in the UTC xsd:datetime format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


from annotation import Annotation

assert Annotation
