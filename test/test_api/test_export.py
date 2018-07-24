# -*- coding: utf-8 -*-

import json
from nose.tools import *
from freezegun import freeze_time
from base import Test, with_context
from factories import AnnotationFactory
from flask import current_app, url_for


class TestExportAPI(Test):

    def setUp(self):
        super(TestExportAPI, self).setUp()
        assert_dict_equal.__self__.maxDiff = None

    @with_context
    @freeze_time("1984-11-19")
    def test_404_exporting_unknown_collection(self):
        """Test 404 exporting unknown Collection."""
        endpoint = '/export/foo/'
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 404, res.data)

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_exported(self):
        """Test Collection exported."""
        annotation = AnnotationFactory()
        endpoint = u'/export/{}/'.format(annotation.collection.id)
        res = self.app_get_json_ld(endpoint)
        assert_equal(res.status_code, 200, res.data)
        data = json.loads(res.data.decode('utf8'))
        assert_equal(data, [
            {
                'id': url_for('api.annotations',
                              collection_id=annotation.collection.id,
                              annotation_id=annotation.id),
                'type': 'Annotation',
                'body': annotation.data['body'],
                'target': annotation.data['target'],
                'created': '1984-11-19T00:00:00Z',
                'generated': '1984-11-19T00:00:00Z',
                'generator': current_app.config.get('GENERATOR')
            }
        ])

    @with_context
    @freeze_time("1984-11-19")
    def test_collection_exported_as_zip(self):
        """Test Collection exported as zip.

        Testing of this really ought to be improved!
        """
        annotation = AnnotationFactory()
        endpoint = u'/export/{}/?zip=1'.format(annotation.collection.id)
        res = self.app.get(endpoint)
        assert_equal(res.headers['Content-Type'], 'application/zip')
        content_disposition = 'attachment; filename=collection1.zip'
        assert_equal(res.headers['Content-Disposition'], content_disposition)
