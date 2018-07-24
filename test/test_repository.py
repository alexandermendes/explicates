# -*- coding: utf8 -*-

from nose.tools import *
from base import Test, db, with_context

from explicates.core import repo
from explicates.model.annotation import Annotation
from explicates.model.collection import Collection


class TestRepository(Test):

    def setUp(self):
        super(TestRepository, self).setUp()

    def test_wrong_object_not_saved(self):
        """Test that the wrong object cannot be saved."""
        annotation = Annotation(data={
            'body': 'foo',
            'target': 'bar'
        })
        assert_raises(ValueError, repo.save, Collection, annotation)

    def test_wrong_object_not_updated(self):
        """Test that the wrong object cannot be updated."""
        annotation = Annotation(data={
            'body': 'foo',
            'target': 'bar'
        })
        assert_raises(ValueError, repo.update, Collection, annotation)

    @with_context
    def test_count_does_not_include_deleted_collections(self):
        """Test count does not include deleted AnnotationCollections."""
        collection1 = Collection()
        collection2 = Collection(deleted=True)
        db.session.add(collection1)
        db.session.add(collection2)
        db.session.commit()
        n = repo.count(Collection)
        assert_equal(n, 1)

    @with_context
    def test_count_does_not_include_deleted_annotations(self):
        """Test count does not include deleted Annotations."""
        collection = Collection()
        anno1 = Annotation(deleted=True, collection=collection, data={
            'body': 'foo',
            'target': 'bar'
        })
        anno2 = Annotation(deleted=False, collection=collection, data={
            'body': 'foo',
            'target': 'bar'
        })
        db.session.add(anno1)
        db.session.add(anno2)
        db.session.commit()
        n = repo.count(Annotation)
        assert_equal(n, 1)
