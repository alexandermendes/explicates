# -*- coding: utf8 -*-

import json
from nose.tools import *
from base import Test, db
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

    def test_range_clauses_with_invalid_key(self):
        """Test range clauses with invalid JSON."""
        data = '{"foo": "bar"}'
        assert_raises(InvalidRequestError, self.search._get_range_clauses,
                      data)

    def test_range_clauses_with_invalid_operator(self):
        """Test range clauses with invalid operator."""
        data = '{"created": {"foo": "bar"}}'
        assert_raises(ValueError, self.search._get_range_clauses, data)

    def test_range_clauses_with_invalid_json(self):
        """Test range clauses with invalid JSON."""
        data = '{""}'
        assert_raises(ValueError, self.search._get_range_clauses, data)

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

    def test_search_by_range_gt(self):
        """Test search by range greater than."""
        anno = AnnotationFactory()
        AnnotationFactory()
        range_query = {
            'created': {
                'gt': anno.created
            }
        }
        results = self.search.search(range=range_query)
        assert_equal(results, [])
