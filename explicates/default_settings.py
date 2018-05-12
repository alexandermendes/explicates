# -*- coding: utf8 -*-
ENV = 'development'
HOST = '0.0.0.0'
PORT = 3000
SQLALCHEMY_TRACK_MODIFICATIONS = False
STRICT_SLASHES = False
ANNOTATIONS_PER_PAGE = 1000
CORS_RESOURCES = {
    r"*": {
        "origins": "*",
        "allow_headers": [
            'Content-Type',
            'Authorization'
        ],
        "max_age": 21600
    }
}
