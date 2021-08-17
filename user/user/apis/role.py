#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from flask_restx import Namespace, Resource, fields


from pony.orm import *
from tools.auth import check_authorization
from tools.db import db

class RoleDAO(db.Entity):
    _table_ = "role"
    id = PrimaryKey(int, auto=True)
    lib = Required(str)
    user = Set("UserDAO")

from .user import RoleDAO



api = Namespace('role', description='Role')



roleModel = api.model('Role',{
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
class roleList(Resource):
    """Shows a list of all roles"""
    @api.doc("role_user")
    @db_session
    @api.marshal_list_with(roleModel)
    def get(self):
        """List all roles"""
        roles = select(p for p in RoleDAO)[:]
        result = {'data': [p.to_dict() for p in roles]}
        return result['data']

    
    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self):
        """Delete all role"""
        RoleDAO.select().delete(bulk=True)
        commit()
        return "", 204

    @api.doc("create_role")
    @api.expect(roleModel, validate=True)
    @api.marshal_with(roleModel, code=201)
    @db_session
    def post(self):
        """Create a new role"""
        payload = api.payload
        role = RoleDAO(**payload)
        commit()
        return role, 201


@check_authorization
@api.route("/<string:id>")
@api.response(404, "role not found")
@api.param("id", "The role  identifier")
class Role(Resource):
    """Show a single role item and lets you delete them"""
    @api.doc("get_role")
    @api.marshal_with(roleModel)
    def get(self, id):
        """Fetch a given role"""
        try:
            user = RoleDAO[id]
            return user
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"Role with id {id} doesn't exist")

    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self, id):
        """Delete a role given its identifier"""
        try:
            RoleDAO[id].delete()
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"Role {id} doesn't exist")
        return "", 204

    @api.doc("update_role")
    @api.expect(roleModel)
    @api.marshal_with(roleModel)
    def put(self, id):
        """Update a given role"""
        payload = api.payload
        if 'id' in payload:
            payload.pop('id')
        try:
            RoleDAO[id].set(**payload)
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"Role with id {id} doesn't exist")
        commit()
        return RoleDAO[id]