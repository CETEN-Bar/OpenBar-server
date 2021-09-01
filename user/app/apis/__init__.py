#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint
from flask_restx import Api
from apis.role import api as nsrole
from apis.user import api as nsuser
from apis.recharge import api as nr

from apis.role import create_tables as create_tables_role
from apis.user import create_tables as create_tables_user
from apis.recharge import create_tables as create_tables_r

apis = Blueprint("apis", __name__, url_prefix="/api/v0")
api = Api(apis,
    title='User API',
    version='1.0',
    description='An API providing functions for User managment',
)
api.add_namespace(nsuser, path='/user')
api.add_namespace(nsrole, path='/user/role')
api.add_namespace(nr, path='/user/recharge')

def create_tables():
    "Create tables for this module"
    create_tables_role()
    create_tables_user()
    create_tables_r()
