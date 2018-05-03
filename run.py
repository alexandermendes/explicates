# -*- coding: utf-8 -*-

from pywa.core import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(port=app.config['PORT'])
else:
    app = create_app()
