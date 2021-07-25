#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""

import os
from flask import Flask, g

from werkzeug.middleware.proxy_fix import ProxyFix

from apis import apis
from tools.db import db

def create_app():
    """Return the flask app for the example microservice"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['RESTPLUS_VALIDATE'] = True

    app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("SQLALCHEMY_DATABASE_URI", default="sqlite:///:memory:")
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'future': True}
    db.init_app(app)
    
    app.register_blueprint(apis)
    return app


if __name__ == '__main__':
    create_app().run(debug=True)
