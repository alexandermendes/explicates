# -*- coding: utf8 -*-

import json
from nose.tools import *
from base import Test, db, with_context
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql import and_
from datetime import datetime, timedelta

from factories import AnnotationFactory
from explicates.search import Search


class TestSearch(Test):

    def setUp(self):
        super(TestSearch, self).setUp()
        self.search = Search(db)

    def test_collection_clause(self):
        """Test collection clause."""
        iri = 'foo'
        clause = self.search._get_collection_clause(iri)
        assert_equal(str(clause), 'collection.id = :id_1')

    @with_context
    def test_search_by_collection(self):
        """Test search by collection."""
        anno = AnnotationFactory()
        AnnotationFactory()
        collection_iri = anno.collection.id
        results = self.search.search(collection=collection_iri)
        assert_equal(results, [anno])

    def test_contains_clause(self):
        """Test contains clause."""
        data = '{"foo": "bar"}'
        clause = self.search._get_contains_clause(data)
        assert_equal(str(clause), 'annotation._data @> :_data_1')

    def test_contains_clause_with_invalid_json(self):
        """Test get contains with invalid JSON."""
        data = '{""}'
        assert_raises(ValueError, self.search._get_contains_clause, data)

    @with_context
    def test_search_by_contains(self):
        """Test search by contains."""
        data = {'foo': 'bar'}
        anno = AnnotationFactory(data=data)
        AnnotationFactory(data={'baz': 'qux'})
        results = self.search.search(contains=data)
        assert_equal(results, [anno])

    def test_ranges_clause(self):
        """Test range clauses."""
        data = {
            'created': {
                'gte': 'foo',
                'lte': 'foo',
                'gt': 'foo',
                'lt': 'foo'
            }
        }
        clauses = self.search._get_range_clauses(json.dumps(data))
        assert_equal(str(and_(*clauses)), (
            'annotation.created >= :created_1 '
            'AND annotation.created <= :created_2 '
            'AND annotation.created > :created_3 '
            'AND annotation.created < :created_4'
        ))

    def test_range_clauses_with_invalid_settings(self):
        """Test range clauses with invalid settings."""
        data = '{"foo": "bar"}'
        assert_raises(ValueError, self.search._get_range_clauses, data)

    def test_range_clauses_with_invalid_operator(self):
        """Test range clauses with invalid operator."""
        data = '{"created": {"foo": "bar"}}'
        assert_raises(ValueError, self.search._get_range_clauses, data)

    def test_range_clauses_with_invalid_json(self):
        """Test range clauses with invalid JSON."""
        data = '{""}'
        assert_raises(ValueError, self.search._get_range_clauses, data)

    @with_context
    def test_search_by_range_lt(self):
        """Test search by range less than."""
        anno_now = AnnotationFactory()
        now = datetime.utcnow()
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        anno_yesterday = AnnotationFactory(created=yesterday)
        AnnotationFactory()
        range_query = {
            'created': {
                'lt': anno_now.created
            }
        }
        results = self.search.search(range=range_query)
        assert_equal(results, [anno_yesterday])

    @with_context
    def test_search_by_range_gt(self):
        """Test search by range greater than."""
        anno = AnnotationFactory(data={'body': 43})
        AnnotationFactory()
        range_query = {
            'body': {
                'gt': 42
            }
        }
        results = self.search.search(range=range_query)
        assert_equal(results, [anno])

    def test_fts_clauses_with_invalid_json(self):
        """Test fts clauses with invalid JSON."""
        data = '{""}'
        assert_raises(ValueError, self.search._get_fts_clauses, data)

    @with_context
    def test_search_by_fts_default(self):
        """Test search by fts with default settings."""
        anno1 = AnnotationFactory(data={'body': {'source': 'foo'}})
        anno2 = AnnotationFactory(data={'body': 'bar'})
        fts_query = {
            'body': {
                'query': 'fo'
            }
        }
        results = self.search.search(fts=fts_query)
        assert_equal(results, [anno1])

    @with_context
    def test_search_by_fts_without_prefix(self):
        """Test search by fts without prefix."""
        anno1 = AnnotationFactory(data={'body': 'qux'})
        AnnotationFactory(data={'body': 'quxx'})
        fts_query = {
            'body': {
                'query': 'qux',
                'prefix': False
            }
        }
        results = self.search.search(fts=fts_query)
        assert_equal(results, [anno1])

    @with_context
    def test_search_by_fts_default_with_or(self):
        """Test search by fts with default settings with or."""
        anno1 = AnnotationFactory(data={'body': {'source': 'foo'}})
        anno2 = AnnotationFactory(data={'body': 'bar'})
        anno3 = AnnotationFactory(data={'body': 'baz'})
        fts_query = {
            'body': {
                'query': 'foo bar',
                'operator': 'or'
            }
        }
        results = self.search.search(fts=fts_query)
        assert_equal(results, [anno1, anno2])

    @with_context
    def test_search_by_fts_phrase(self):
        """Test search by fts phrase."""
        anno1 = AnnotationFactory(data={'body': {'source': 'foo bar baz'}})
        anno2 = AnnotationFactory(data={'body': 'foo bar baz qux'})
        AnnotationFactory(data={'body': 'foo baz'})
        fts_phrase_query = {
            'body': {
                'query': 'foo bar baz'
            }
        }
        results = self.search.search(fts_phrase=fts_phrase_query)
        assert_equal(results, [anno1, anno2])

    @with_context
    def test_search_by_fts_phrase_with_distance(self):
        """Test search by fts phrase with distance."""
        anno1 = AnnotationFactory(data={'body': 'foo bar baz qux'})
        AnnotationFactory(data={'body': 'foo bar qux'})
        AnnotationFactory(data={'body': 'foo qux'})
        fts_phrase_query = {
            'body': {
                'query': 'foo qux',
                'distance': 3
            }
        }
        results = self.search.search(fts_phrase=fts_phrase_query)
        assert_equal(results, [anno1])
