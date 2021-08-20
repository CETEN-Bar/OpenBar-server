#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""
import os
from flask import Flask
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from tools.db import db_wrapper
from tools.socketio import socketio

from apis import apis
from apis import create_tables as create_tables_apis

def create_app():
    """Return the flask app for the example microservice"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['RESTPLUS_VALIDATE'] = True
    
    app.register_blueprint(apis)

    app.config['DATABASE'] = os.environ.get('DATABASE', default="sqlite:///:memory:")
    db_wrapper.init_app(app)

    with db_wrapper.database.connection_context():
        create_tables_apis()

    socketio.init_app(app)
    return app



if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
