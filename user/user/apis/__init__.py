#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

import os
from flask import Flask, g, Blueprint
from pony.flask import Pony
from flask_socketio import SocketIO
from flask_restx import Api
from tools.db import db, initdb
from werkzeug.middleware.proxy_fix import ProxyFix

socketio = SocketIO(cors_allowed_origins="*")
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






from apis.role import api as nsrole
from apis.user import api as nsuser


apis = Blueprint("apis", __name__, url_prefix="/api/v0")
api = Api(apis,
    title='User API',
    version='1.0',
    description='An API providing functions for User managment',
)

api.add_namespace(nsuser, path='/user')
api.add_namespace(nsrole, path='/role')

