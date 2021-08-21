#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the API
"""

from flask import Blueprint
from flask_restx import Api

from apis.basic import api as nsbasic
from apis.db import api as nsdb

from apis.db import create_tables as create_tables_db

apis = Blueprint("apis", __name__, url_prefix="/api/v0/example")
api = Api(apis,
    title='Example API',
    version='1.0',
    description='An example API providing examples about how to build an API',
)

api.add_namespace(nsbasic, path='/basic')
api.add_namespace(nsdb, path='/db')

def create_tables():
    "Create tables for this module"
    create_tables_db()
