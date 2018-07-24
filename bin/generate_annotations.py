#!/usr/bin/env python

import sys

from explicates.core import db, create_app
from explicates.model.collection import Collection
from explicates.model.annotation import Annotation


app = create_app()


def generate_annotations(n, collection_key):
    """Add n Annotations to the AnnotationCollection with collection_key."""
    with app.app_context():
        collection = db.session.query(Collection).get(collection_key)
        for i in range(n):
            anno = Annotation(collection=collection)
            db.session.add(anno)
        db.session.commit()


if __name__ == '__main__':
    n = int(sys.argv[1])
    collection_key = int(sys.argv[2])
    generate_annotations(n, collection_key)
