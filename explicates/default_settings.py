# -*- coding: utf8 -*-
ENV = 'development'
HOST = '0.0.0.0'
PORT = 3000
SQLALCHEMY_TRACK_MODIFICATIONS = False
STRICT_SLASHES = False
ANNOTATIONS_PER_PAGE = 1000
CORS_RESOURCES = {
    r"/*": {
        "origins": "*",
        "allow_headers": [
            'Content-Type',
            'Content-Length',
            'Authorization',
            'If-Match',
            'Prefer',
            'Accept',
            'Slug'
        ],
        "max_age": 21600,
        "supports_credentials": True
    }
}
