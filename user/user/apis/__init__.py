#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint,Flask,g
import os
from flask_restx import Api
from flask_socketio import SocketIO
from tools.db import db
from werkzeug.middleware.proxy_fix import ProxyFix

"""Return the flask app for the example microservice"""
app = Flask(__name__)
app.config['SECRET_KEY'] = "testo"
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['RESTPLUS_VALIDATE'] = True

app.config['SQLALCHEMY_DATABASE_URI'] =  os.environ.get("SQLALCHEMY_DATABASE_URI", default="sqlite:///:memory:")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'future': True}
db.init_app(app)


socketio = SocketIO(app,cors_allowed_origins="*")


from apis.role import api as nsrole
from apis.user import api as nsuser


apis = Blueprint("apis", __name__, url_prefix="/api/v0")
api = Api(apis,
    title='User API',
    version='1.0',
    description='An  API providing functions for User managment',
)

api.add_namespace(nsuser, path='/user')
api.add_namespace(nsrole, path='/role')

app.register_blueprint(apis)

