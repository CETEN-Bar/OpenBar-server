#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API of Roles
"""

from flask_restx import Namespace, Resource, fields
from playhouse.shortcuts import model_to_dict

from models.role import Role
from tools.auth import is_password_logged, is_barman

api = Namespace('role', description='Role')

roleModel = api.model('Role', {
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='Role identifier'),
    'lib': fields.String(
        required=True,
        description='Role description'),
    'is_admin': fields.Boolean(
        required=True,
        description='If the role give user admin rigths',
        example=False),
    'is_barman': fields.Boolean(
        required=True,
        description='If the role give user barman/barwoman rigths',
        example=False),
})


@api.route("/")
class RoleList(Resource):
    """Shows a list of all roles"""
    @api.doc("role_user", security='token')
    @api.marshal_list_with(roleModel)
    def get(self):
        """List all roles"""
        roles = Role.select()
        return [model_to_dict(r) for r in roles]

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("delete_role", security='password')
    @api.response(204, "role deleted")
    def delete(self):
        """Delete all role"""
        Role.delete().execute()
        return "", 204

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("create_role", security='password')
    @api.expect(roleModel, validate=True)
    @api.marshal_with(roleModel, code=201)
    def post(self):
        """Create a new role"""
        payload = {x: api.payload[x] for x in api.payload if x in roleModel}
        if 'id' in payload:
            payload.pop('id')
        role = Role(**payload)
        role.save()
        return model_to_dict(role), 201


@api.route("/<string:id>")
@api.response(404, "role not found")
@api.param("id", "The role  identifier")
class RoleAPI(Resource):
    """Show a single role item and lets you delete them"""
    @api.doc("get_role", security='token')
    @api.marshal_with(roleModel)
    def get(self, id):
        """Fetch a given role"""
        try:
            role = Role[id]
            return model_to_dict(role)
        except Role.DoesNotExist:
            api.abort(404, f"Role with id {id} doesn't exist")

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("delete_role", security='password')
    @api.response(204, "role deleted")
    def delete(self, id):
        """Delete a role given its identifier"""
        try:
            Role[id].delete_instance()
        except Role.DoesNotExist:
            api.abort(404, f"Role {id} doesn't exist")
        return "", 204

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("update_role", security='password')
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
