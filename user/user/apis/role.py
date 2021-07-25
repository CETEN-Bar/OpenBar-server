#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from dateutil import parser

from flask_restx import Namespace, Resource, fields
from sqlalchemy import select, delete, update,ForeignKey
from sqlalchemy.orm import relationship

import bcrypt

from .user import RoleDAO

from tools.auth import check_authorization
from tools.db import db, get_session


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
    @api.marshal_list_with(roleModem)
    def get(self):
        """List all user"""
        roles = get_session().execute(select(RoleDAO)).scalars().all()
        return roles

    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self):
        """Delete all role"""
        ses = get_session()
        ses.execute(delete(RoleDAO))
        ses.commit()
        return "", 204

    @api.doc("create_role")
    @api.expect(roleModem, validate=True)
    @api.marshal_with(roleModem, code=201)
    def post(self):
        """Create a new user"""
        payload = api.payload
        role = RoleDAO(**payload)
        ses = get_session()
        ses.add(role)
        ses.commit()
        return role, 201
