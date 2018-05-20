# -*- coding: utf8 -*-

import os
import json
from functools import wraps

from factories import reset_all_pk_sequences

from explicates.core import create_app, db


os.environ['EXPLICATES_SETTINGS'] = '../settings_test.py'

flask_app = create_app()


def with_context(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        with flask_app.app_context():
            return f(*args, **kwargs)
    return decorated_function


def rebuild_db():
    """Rebuild the DB."""
    db.drop_all()
    db.create_all()


class Test(object):

    def setUp(self):
        self.flask_app = flask_app
        self.app = flask_app.test_client()
        with self.flask_app.app_context():
            rebuild_db()

    def tearDown(self):
        with self.flask_app.app_context():
            db.session.remove()
            reset_all_pk_sequences()

    def app_get_json_ld(self, url, follow_redirects=False, headers=None):
        content_type = 'application/ld+json'
        if not headers:
            headers = {}
        headers['Accept'] = content_type
        return self.app.get(url,
                            follow_redirects=follow_redirects,
                            headers=headers,
                            content_type=content_type)

    def app_post_json_ld(self, url, data=None, follow_redirects=False,
                         headers=None):
        content_type = 'application/ld+json'
        if not headers:
            headers = {}
        headers['Accept'] = content_type
        if data:
            return self.app.post(url,
                                 data=json.dumps(data),
                                 follow_redirects=follow_redirects,
                                 headers=headers,
                                 content_type=content_type)
        else:
            return self.app.post(url,
                                 follow_redirects=follow_redirects,
                                 headers=headers,
                                 content_type=content_type)

    def app_put_json_ld(self, url, data=None, follow_redirects=False,
                        headers=None):
        content_type = 'application/ld+json'
        if not headers:
            headers = {}
        headers['Accept'] = content_type
        if data:
            return self.app.put(url,
                                data=json.dumps(data),
                                follow_redirects=follow_redirects,
                                headers=headers,
                                content_type=content_type)
        else:
            return self.app.put(url,
                                follow_redirects=follow_redirects,
                                headers=headers,
                                content_type=content_type)

    def app_delete_json_ld(self, url, follow_redirects=False, data=None,
                           headers=None):
        content_type = 'application/ld+json'
        if not headers:
            headers = {}
        headers['Accept'] = content_type
        return self.app.delete(url,
                               follow_redirects=follow_redirects,
                               headers=headers,
                               data=json.dumps(data),
                               content_type=content_type)
