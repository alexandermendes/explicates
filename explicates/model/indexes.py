# -*- coding: utf-8 -*-
"""Indexes."""

from sqlalchemy.schema import Index
from sqlalchemy.sql import text


indexes = [
    Index('idx_annotation_body',
          text("to_tsvector(language::regconfig, _data -> 'body')"),
          postgresql_using='gin'),
    Index('idx_annotation_target',
          text("to_tsvector(language::regconfig, _data -> 'target')"),
          postgresql_using='gin')
]
