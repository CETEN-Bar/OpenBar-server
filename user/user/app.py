#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main functions for the example microservice flask app
"""
import os
from flask import Flask, g
from pony.flask import Pony
from flask_socketio import SocketIO
from flask_restx import Api
from tools.db import db, initdb
from werkzeug.middleware.proxy_fix import ProxyFix
from apis import socketio, apis

def create_app():
    """Return the flask app for the example microservice"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config['RESTPLUS_VALIDATE'] = True
    
    app.register_blueprint(apis)

    app.config.update(dict(
        DEBUG = False,
        SECRET_KEY = 'testo',
        PONY = {
            'provider': 'postgres',
            'host': 'database',
            'database': 'user',
            'port': '5432',
            'password': os.environ.get('DB_PASSWORD'),
            'user':'service_user'
        }
    ))
    initdb(app)
    Pony(app)
    socketio.init_app(app)
    return app



if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
