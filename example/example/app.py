#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""

import os
from flask import Flask, g
from pony.flask import Pony
from tools.db import db, initdb

from werkzeug.middleware.proxy_fix import ProxyFix

from apis import apis

def create_app():
    """Return the flask app for the example microservice"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['RESTPLUS_VALIDATE'] = True
    
    app.register_blueprint(apis)

    app.config.update(dict(
    PONY = {
        'provider': 'postgres',
        'host': 'database',
        'database': 'example',
        'port': '5432',
        'password': os.environ.get('DB_PASSWORD'),
        'user':'service_example'
        }
    ))
    initdb(app)
    Pony(app)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
