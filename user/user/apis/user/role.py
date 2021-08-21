#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from flask_restx import Resource, fields

from peewee import *
from playhouse.shortcuts import model_to_dict

from tools.auth import check_authorization
from tools.db import db_wrapper

from apis.user import api

class Role(db_wrapper.Model):
    _table_ = "role"
    id = AutoField()
    lib = CharField()

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
@api.route("/role/")
class RoleListAPI(Resource):
    """Shows a list of all roles"""
    @api.doc("role_user")
    @api.marshal_list_with(roleModel)
    def get(self):
        """List all roles"""
        roles = Role.select()
        return [model_to_dict(r) for r in roles]

    
    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self):
        """Delete all role"""
        Role.delete().execute()
        return "", 204

    @api.doc("create_role")
    @api.expect(roleModel, validate=True)
    @api.marshal_with(roleModel, code=201)
    def post(self):
        """Create a new role"""
        payload = {x: api.payload[x] for x in api.payload if x in roleModel}
        role = Role(**payload)
        role.save()
        return model_to_dict(role), 201


@check_authorization
@api.route("/role/<string:id>")
@api.response(404, "role not found")
@api.param("id", "The role  identifier")
class RoleAPI(Resource):
    """Show a single role item and lets you delete them"""
    @api.doc("get_role")
    @api.marshal_with(roleModel)
    def get(self, id):
        """Fetch a given role"""
        try:
            role = Role[id]
            return model_to_dict(role)
        except Role.DoesNotExist:
            api.abort(404, f"Role with id {id} doesn't exist")

    @api.doc("delete_role")
    @api.response(204, "role deleted")
    def delete(self, id):
        """Delete a role given its identifier"""
        try:
            Role[id].delete_instance()
        except Role.DoesNotExist:
            api.abort(404, f"Role {id} doesn't exist")
        return "", 204

    @api.doc("update_role")
    @api.expect(roleModel)
    @api.marshal_with(roleModel)
    def put(self, id):
        """Update a given role"""
        payload = {x: api.payload[x] for x in api.payload if x in roleModel}
        if 'id' in payload:
            payload.pop('id')
        try:
            if len(payload) == 0:
                return model_to_dict(Role[id])
            Role.update(**payload).where(Role.id == id).execute()
            return Role[id]
        except Role.DoesNotExist:
            api.abort(404, f"Role with id {id} doesn't exist")
