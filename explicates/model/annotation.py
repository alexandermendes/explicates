# -*- coding: utf8 -*-
"""Annotation model."""

from flask import url_for, current_app
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base

from explicates.core import db
from explicates.model.base import BaseDomainObject


Base = declarative_base(cls=BaseDomainObject)


def get_language(context):
    """Return the language to be used for full-text searches."""
    data = context.current_parameters.get('_data')

    # Map of the available PostgreSQL dictionaries
    lang_map = current_app.config['FTS_LANGUAGE_MAP']

    if data and data.get('body'):
        body = data.get('body')
        if isinstance(body, list):
            body = body[0]
        if not isinstance(body, dict):
            return current_app.config['FTS_DEFAULT']

        lang = body.get('language')
        if not lang:
            return current_app.config['FTS_DEFAULT']
        if isinstance(lang, list):
            lang = lang[0]
        try:
            # Get lang code from the BCP47 spec recommended for
            # Web Annotations (e.g. en-US)
            lang_code = lang.split('-')[0]
            return lang_map[lang_code]
        except KeyError:
            return current_app.config['FTS_DEFAULT']
    return current_app.config['FTS_DEFAULT']


class Annotation(db.Model, Base):
    """An Annotation"""

    __tablename__ = 'annotation'

    #: The related Collection ID.
    collection_key = Column(Integer, ForeignKey('collection.key'),
                            nullable=False)

    #: The language used for full-text searches.
    language = Column(String, nullable=False, default=get_language)

    @hybrid_property
    def iri(self):
        if self.id:
            return url_for('api.annotations', collection_id=self.collection.id,
                           annotation_id=self.id, _external=True)
