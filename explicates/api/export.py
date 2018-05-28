# -*- coding: utf8 -*-
"""Export API module."""

import unidecode
import zipfile
import zipstream
from flask import Response, abort, request, stream_with_context
from flask.views import MethodView

from explicates.core import exporter
from explicates.api.base import APIBase
from explicates.model.collection import Collection


class ExportAPI(APIBase, MethodView):
    """Export API class."""

    # Common headers for all responses
    headers = {
        'Allow': 'GET,OPTIONS,HEAD'
    }

    def _get_zip_compression(self):
        """Return the available ZIP compression."""
        try:
            import zlib
            assert zlib
            return zipfile.ZIP_DEFLATED
        except Exception as ex:  # pragma: no cover
            return zipfile.ZIP_STORED

    def _ascii_encode(self, collection_id):
        """Ensure a collection_id is ASCII encoded."""
        name = unidecode.unidecode(collection_id)
        return name

    def _zip_response(self, collection_id, generator):
        """Respond with a ZIP file."""
        compression = self._get_zip_compression()
        z = zipstream.ZipFile(mode='w', compression=compression)
        safe_name = self._ascii_encode(collection_id)
        json_fn = safe_name + '.json'
        zip_fn = safe_name + '.zip'
        z.write_iter(json_fn, generator)
        response = Response(stream_with_context(z), mimetype='application/zip')
        content_disposition = 'attachment; filename={}'.format(zip_fn)
        response.headers['Content-Disposition'] = content_disposition
        return response

    def get(self, collection_id):
        """Export the contents of an AnnotationCollection."""
        collection = self._get_domain_object(Collection, collection_id)
        if not collection:
            abort(404)

        _zip = request.args.get('zip')

        data_gen = exporter.generate_data(collection.id)
        if _zip == '1':
            return self._zip_response(collection_id, data_gen)

        return Response(stream_with_context(data_gen),
                        mimetype='application/ld+json')
