# -*- coding: utf-8 -*-

from pywa.core import create_app


if __name__ == "__main__":
    app = create_app()
    app.run()
else:
    app = create_app()
