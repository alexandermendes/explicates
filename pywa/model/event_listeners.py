# -*- coding: utf8 -*-

import os
import json
from jsonschema import validate as validate_json
from jsonschema.exceptions import ValidationError
from sqlalchemy import event

from pywa.model.annotation import Annotation
from pywa.model.collection import Collection


def validate(obj, schema_filename):
    """Validate a JSON object according to the given schema."""
    here = os.path.dirname(os.path.abspath(__file__))
    schemas_dir = os.path.join(os.path.dirname(here), 'schemas')
    schema_path = os.path.join(schemas_dir, schema_filename)
    with open(schema_path, 'rb') as json_file:
        schema = json.load(json_file)
        validate_json(obj, schema)

@event.listens_for(Annotation, 'before_insert')
@event.listens_for(Annotation, 'before_update')
def validate_annotation(mapper, conn, target):
    """Validate an Annotation before INSERT or UPDATE."""
    validate(target.dictize(), 'annotation.json')

@event.listens_for(Collection, 'before_insert')
@event.listens_for(Collection, 'before_update')
def validate_collection(mapper, conn, target):
    """Validate an Collection before INSERT or UPDATE."""
    validate(target.dictize(), 'collection.json')
