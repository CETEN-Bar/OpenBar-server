#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint
from flask_restx import Api

from tools.auth import TokenAuthError, PasswordAuthError, WWW_AUTH_TOKEN_HEADER, WWW_AUTH_HEADER_PASSWORD, authorizations

from apis.role import api as nsrole
from apis.user import api as nsuser
from apis.recharge import api as nsrecharge
from apis.order import api as nsorder
from apis.auth import api as nsauth

apis = Blueprint("apis", __name__, url_prefix="/api/v0")
api = Api(apis,
    title='User API',
    version='1.0',
    description='An API providing functions for User managment',
    authorizations=authorizations
)

api.add_namespace(nsauth, path='/user/auth')
api.add_namespace(nsuser, path='/user')
api.add_namespace(nsrole, path='/user/role')
api.add_namespace(nsrecharge, path='/user/recharge')
api.add_namespace(nsorder, path='/order')

@api.errorhandler(TokenAuthError)
@api.header('WWW-Authenticate',  'Authentification information')
def failed_token_auth_response(error):
    "Create response in case of a failed authentification by token"
    return {'message': error.message}, error.code, {'WWW-Authenticate': WWW_AUTH_TOKEN_HEADER}


@api.errorhandler(PasswordAuthError)
@api.header('WWW-Authenticate',  'Authentification information')
def failed_password_auth_response(error):
    "Create response in case of a failed authentification by password"
    return {'message': error.message}, error.code, {'WWW-Authenticate': WWW_AUTH_HEADER_PASSWORD}
