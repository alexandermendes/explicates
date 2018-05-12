# -*- coding: utf-8 -*-

from explicates.core import create_app


if __name__ == "__main__":
    app = create_app()
    debug = False
    if app.config['DEBUG'] or app.config['ENV'] == 'development':
        debug = True
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=debug)
else:
    app = create_app()
