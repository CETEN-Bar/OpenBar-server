#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint
from flask_restx import Api
from apis.user import api as nsuser

from apis.user.create_tables import create_tables as create_tables_user

apis = Blueprint("apis", __name__, url_prefix="/api/v0")
api = Api(apis,
    title='User API',
    version='1.0',
    description='An API providing functions for User managment',
)

api.add_namespace(nsuser, path='/user')

def create_tables():
    "Create tables for this module"
    create_tables_user()
