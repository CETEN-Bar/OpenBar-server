#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from typing import Optional
from dateutil import parser

from flask_restx import Namespace, Resource, fields
from pony.orm import *
from flask_socketio import send, SocketIO
from flask import g
import bcrypt
import sys
from tools.socketio import socketio


from tools.auth import check_authorization
from tools.db import db


local_history= []

api = Namespace('user', description='User')


class RoleDAO(db.Entity):
    _table_ = "role"
    id = PrimaryKey(int, auto=True)
    lib = Required(str)
    user = Set("UserDAO")


class UserDAO(db.Entity):
    """user object"""
    _table_ = "user_table"
    id = PrimaryKey(int, auto=True)
    id_card = Required(str)
    name = Required(str)
    fname = Required(str)
    balance = Required(int)
    role = Required(RoleDAO,column="bid")
    username = Optional(str)
    password = Optional(str)


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
        attribute= lambda x: x.role.get_pk() if type(x) != dict else x.get('role')) ,
    'username': fields.String(
        required=False,
        description='Username'),
    'password': fields.String(
        required=False,
        description='Password'),
})


@check_authorization
@api.route("/")
class userList(Resource):
    """Shows a list of all user"""
    @api.doc("list_user")
    @api.marshal_list_with(userModel)
    @db_session
    def get(self):
        """List all user"""
        users = UserDAO.select()
        result = {'data': [p.to_dict() for p in users]}
        return result['data']


    @api.doc("create_user")
    @api.expect(userModel, validate=False)
    @api.marshal_with(userModel, code=201)
    @db_session
    def post(self):
        """Create a new user"""
        payload = api.payload
        payload['id_card'] = str(bcrypt.hashpw(str.encode(payload['id_card']),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))
        user = UserDAO(**payload)
        user.role = user.role.id
        commit()
        return user, 201


@check_authorization
@api.route("/<string:id_card>")
@api.response(404, "user not found")
@api.param("id_card", "The user card identifier")
class User(Resource):
    """Show a single user item and lets you delete them"""
    @api.doc("get_user")
    @api.marshal_with(userModel)
    @socketio.on("message")
    def get(self, id_card):
        """Fetch a given user"""
        try:
            user = UserDAO.select(lambda u : u.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))).first()
            local_history.insert(0,user.name+" "+user.fname)
            socketio.send(user.to_dict())
            return user
        except AttributeError:
            socketio.send({'message':'new user'})
            local_history.insert(0,"*******")
            api.abort(404, f"User with id card {id_card} doesn't exist")
            


    @api.doc("delete_user")
    @api.response(204, "task deleted")
    def delete(self, id_card):
        """Delete a user given its identifier"""
        try:
            UserDAO.select(lambda u : u.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))).first().delete()
            commit()
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"User with id card {id_card} doesn't exist")
        return "", 204

    @api.expect(userModel)
    @api.marshal_with(userModel)
    def put(self, id_card):
        """Update a user given its identifier"""
        payload = api.payload
        if 'id' in payload:
            payload.pop('id')
        if 'id_card' in payload:
            payload.pop('id_card')
        user = UserDAO.select(lambda u : u.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))).first()
        try:
           user.set(**payload)
        except pony.orm.core.ObjectNotFound:
            api.abort(404, f"User {id} doesn't exist")
        commit()
        return user


@check_authorization
@api.route("/history")
class History(Resource):
    """Show the history of the NFC card reader. This history will reset each time you restart the app"""
    @api.doc("get_history")
    def get(self):
        """Fetch the history"""
        return local_history
            

