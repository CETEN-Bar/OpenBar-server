#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

import sys
from typing import Optional
from dateutil import parser
import bcrypt

from flask import g
from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict
from flask_socketio import send, SocketIO
from tools.socketio import socketio

from tools.auth import check_authorization
from tools.db import db_wrapper
from apis.role import Role

local_history = []

api = Namespace('user', description='User')



class User(db_wrapper.Model):
    """user object"""
    _table_ = "user_table"
    id = AutoField()
    id_card = CharField(unique=True)
    name = CharField()
    fname = CharField()
    balance = IntegerField()
    role = ForeignKeyField(Role, backref="users")
    group_year = IntegerField()
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
        payload['id_card'] = str(bcrypt.hashpw(str.encode(payload['id_card']),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))
        userobj = User(**payload)
        userobj.save()
        user = model_to_dict(userobj)
        print(user)
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
    @socketio.on("message")
    def get(self, id_card):
        """Fetch a given user"""
        user_id = False
        for u in User.select(User.id, User.id_card):
            if u.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.')):
                user_id = u.id
                break
        if not user_id:
            socketio.send({'message':'new user'})
            local_history.insert(0,"*******")
            api.abort(404, f"User with id card {id_card} doesn't exist")
        user = User[user_id]
        local_history.insert(0,user.name + " " + user.fname)
        user = model_to_dict(user)
        socketio.send(user)
        return user


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

def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([User])
