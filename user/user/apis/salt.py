#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from flask_restx import Namespace, Resource, fields

import sys
from pony.orm import *
from tools.auth import check_authorization
from tools.db import db

class SaltDAO(db.Entity):
    _table_ = "salt"
    id = PrimaryKey(int)
    salt = Required(str)
    user = Set("UserDAO")



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
class saltList(Resource):
    """Shows a list of all salt"""
    @api.doc("get_salt")
    @db_session
    @api.marshal_list_with(saltModel)
    def get(self):
        """List all salt"""
        salt = SaltDAO.select()
        return [t.to_dict() for t in salt]
    
    @api.doc("create_salt")
    @api.expect(saltModel, validate=True)
    @api.marshal_with(saltModel, code=201)
    @db_session
    def post(self):
        """Create a new salt"""
        payload = api.payload
        payload['salt'] = payload['salt'][1:].replace('\'','')
        role = SaltDAO(**payload)
        commit()
        return role, 201

@check_authorization
@api.route("/<string:year>")
@api.response(404, "salt not found")
@api.param("year", "The year of the salt")
class Role(Resource):
    """Show a single salt"""
    @api.doc("get_role")
    @api.marshal_with(saltModel)
    def get(self, year):
        """Fetch a given salt"""
        try:
            salt = saltModel[year]
            return salt
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"Salt with year {year} doesn't exist")
