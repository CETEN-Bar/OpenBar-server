#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

import sys

from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict

from tools.auth import check_authorization
from tools.db import db_wrapper

class Salt(db_wrapper.Model):
    year = IntegerField(primary_key=True)
    salt = CharField()

api = Namespace('salt', description='salt')

saltModel = api.model('Salt',{
    'id': fields.Integer(
        attribute='id',
        required=True,
        description='Salt year attribution'),
    'salt': fields.String(
        required=True,
        attribute='salt',
        description='Salt'),
})

@check_authorization
@api.route("/")
class SaltListAPI(Resource):
    """Shows a list of all salt"""
    @api.doc("get_salt")
    @api.marshal_list_with(saltModel)
    def get(self):
        """List all salt"""
        salts = Salt.select()
        return [model_to_dict(s) for s in salts]
    
    @api.doc("create_salt")
    @api.expect(saltModel, validate=True)
    @api.marshal_with(saltModel, code=201)
    def post(self):
        """Create a new salt"""
        payload = {x: api.payload[x] for x in api.payload if x in saltModel}
        payload['salt'] = payload['salt'][1:].replace('\'','')
        salt = Salt(**payload)
        salt.save()
        return model_to_dict(salt), 201

@check_authorization
@api.route("/<string:year>")
@api.response(404, "salt not found")
@api.param("year", "The year of the salt")
class SaltAPI(Resource):
    """Show a single salt"""
    @api.doc("get_role")
    @api.marshal_with(saltModel)
    def get(self, year):
        """Fetch a given salt"""
        try:
            salt = Salt[year]
            return model_to_dict(salt)
        except Salt.DoesNotExist:
            api.abort(404, f"Salt with year {year} doesn't exist")
