#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

import sys
import bcrypt
import requests
from dateutil import parser
from datetime import date

from flask_restx import Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict

from tools.auth import check_authorization
from tools.db import db_wrapper
from apis.user.role import Role
from apis.user.salt import Salt


from apis.user import api

local_history = []


class User(db_wrapper.Model):
    """user object"""
    id = AutoField()
    id_card = CharField(unique=True)
    name = CharField()
    fname = CharField()
    balance = IntegerField()
    role = ForeignKeyField(Role, backref="users")
    salt = ForeignKeyField(Salt, backref="users")
    group_year = IntegerField(null=True)
    username = CharField(null=True)
    password = CharField(null=True)


userModel = api.model('User', {
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='User identifier'),
    'id_card': fields.String(
        required=True,
        description='User card identifier'),
    'name': fields.String(
        required=True,
        description='User name'),
    'fname': fields.String(
        required=True,
        description='User first name'),
    'balance': fields.Integer(
        required=True,
        description='User balance, multiplied by 100'),
    'role': fields.Integer(
        required=True,
        example=1,
        description='User\'s role identifier',
        attribute= lambda x: x if type(x) != dict else x['role']['id']),
    'salt_year': fields.Integer(
        required=True,
        description='Salt year',
        attribute= lambda x: x if type(x) != dict else x['salt']['year']),
    'group_year': fields.Integer(
        required=False,
        example=2023,
        description='User\'s group year'
    ),
    'username': fields.String(
        required=False,
        description='Username'),
    'password': fields.String(
        required=False,
        description='Password'),
})


@check_authorization
@api.route("/")
class UserListAPI(Resource):
    """Shows a list of all user"""
    @api.doc("list_user")
    @api.marshal_list_with(userModel)
    def get(self):
        """List all user"""
        users = User.select()
        return [model_to_dict(u) for u in users]


    @api.doc("create_user")
    @api.expect(userModel, validate=False)
    @api.marshal_with(userModel, code=201)
    def post(self):
        """Create a new user"""
        payload = {x: api.payload[x] for x in api.payload if x in userModel}
        if 'id' in payload:
            payload.pop('id')
        try:
            payload['salt'] = Salt[date.today().year]
        except Salt.DoesNotExist:
            myobj = {"year": date.today().year, "salt": str(bcrypt.gensalt())[1:].replace('\'','')}
            payload['salt'] = Salt(**myobj)
            payload['salt'].save()
        payload['id_card'] =  str(bcrypt.hashpw(str.encode(payload['id_card']),bytes(payload['salt'].salt.replace('"', '\''),encoding='utf8')))
        userobj = User(**payload)
        userobj.save()
        user = model_to_dict(userobj)
        user['role'] = userobj.role.id
        return user, 201

@check_authorization
@api.route("/<string:id_card>")
@api.response(404, "user not found")
@api.param("id_card", "The user card identifier")
class UserAPI(Resource):
    """Show a single user item and lets you delete them"""
    @api.doc("get_user")
    @api.marshal_with(userModel)
    def get(self, id_card):
        """Fetch a given user"""
        slist = Salt.select().order_by(Salt.id.desc())
        for s in slist:
            salt = bytes(s.salt.replace('"', '\''), encoding='utf8')
            users = User.select(User.salt.year == s.year and User.id_card == str(bcrypt.hashpw(str.encode(id_card), salt)))
            if users.count() > 0:
                user = users[0]
                local_history.insert(0, user.name + " " + user.fname)
                return model_to_dict(user)
        local_history.insert(0, "*******")
        api.abort(404, f"User with id card {id_card} doesn't exist")


    @api.doc("delete_user")
    @api.response(204, "User deleted")
    def delete(self, id):
        """Delete a user given its identifier"""
        try:
            User[id].delete_instance()
        except User.DoesNotExist:
            api.abort(404, f"User with id card {id_card} doesn't exist")
        return "", 204

    @api.expect(userModel)
    @api.marshal_with(userModel)
    def put(self, id):
        """Update a user given its identifier"""
        payload = {x: api.payload[x] for x in api.payload if x in userModel}
        if 'id' in payload:
            payload.pop('id')
        if 'id_card' in payload:
            payload.pop('id_card')
        try:
           User.update(**payload).where(User.id == id).execute()
        except User.DoesNotExist:
            api.abort(404, f"User {id} doesn't exist")
        return user


@check_authorization
@api.route("/history")
class History(Resource):
    """Show the history of the NFC card reader. This history will reset each time you restart the app"""
    @api.doc("get_history")
    def get(self):
        """Fetch the history"""
        return local_history
