#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""
import os
from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from filelock import FileLock

from werkzeug.middleware.proxy_fix import ProxyFix
from tools.db import db_wrapper

from apis import apis
from models import create_tables

db_lock = FileLock("/tmp/db.lock")

def create_app():
    """Return the flask app for the example microservice"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['RESTPLUS_VALIDATE'] = True
    
    app.register_blueprint(apis)


    app.config['DATABASE'] = os.environ.get('DATABASE', default="sqlite:///:memory:")
    db_wrapper.init_app(app)
    app.secret_key = "TestENPROD"

    with db_lock:
        with db_wrapper.database.connection_context():
            create_tables()

    CORS(app)
    return app

if __name__ == '__main__':
    create_app().run(debug=True)
