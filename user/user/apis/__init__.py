#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint,Flask,g
import os
from flask_restx import Api
from flask_socketio import SocketIO
from pony.flask import Pony
from tools.db import db
from werkzeug.middleware.proxy_fix import ProxyFix

"""Return the flask app for the example microservice"""
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['RESTPLUS_VALIDATE'] = True

app.config.update(dict(
    DEBUG = False,
    SECRET_KEY = 'testo',
    PONY = {
        'provider': 'postgres',
        'host': 'database',
        "database":'user',
        'port': '5432',
        'password': os.environ.get('DB_SERVICE_USER_PW'),
        'user':'service_user'
    }
))


socketio = SocketIO(app,cors_allowed_origins="*")


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

app.register_blueprint(apis)
db.bind(**app.config['PONY'])
db.generate_mapping(create_tables=True)
Pony(app)
