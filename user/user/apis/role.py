#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from dateutil import parser

from flask_restx import Namespace, Resource, fields


import bcrypt
from pony.orm import *
from .user import RoleDAO
import sys
import json

from tools.auth import check_authorization
from tools.db import db


api = Namespace('role', description='Role')



roleModem = api.model('Role',{
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='Role identifier'),
    'lib': fields.String(
        required=True,
        description='Role description'),
})

@check_authorization
@api.route("/")
class userList(Resource):
    """Shows a list of all roles"""
    @api.doc("role_user")
    @db_session
    @api.marshal_list_with(roleModem)
    def get(self):
        """List all user"""
        roles = RoleDAO.select()
        return roles

    '''
    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self):
        """Delete all role"""
        ses = get_session()
        ses.execute(delete(RoleDAO))
        ses.commit()
        return "", 204
    '''

    @api.doc("create_role")
    @api.expect(roleModem, validate=True)
    @api.marshal_with(roleModem, code=201)
    @db_session
    def post(self):
        """Create a new user"""
        payload = api.payload
        role = RoleDAO(**payload)
        commit()
        return role, 201
