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
import argon2

from flask_restx import Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict
from flask_login import UserMixin, login_required, login_user, logout_user 
from tools.LoginManager import login_manager

from tools.auth import check_authorization
from tools.db import db_wrapper

from apis.user.role import Role
from apis.user.salt import Salt

from apis.user import api

local_history = []


class User(UserMixin,db_wrapper.Model):
    """user object"""
    _table_= "user_table"
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
        attribute= lambda x: x['role'] if type(x['role']) is int else x['role']['id']),
    'salt_year': fields.Integer(
        required=True,
        description='Salt year',
        attribute= lambda x: x['salt'] if type(x['salt']) is int else x['salt']['year'] ),
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

    @login_required
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
            print(payload['salt'].save(force_insert=True),file=sys.stderr)
        if not user_exsist(payload['id_card']):
            payload['id_card'] =  str(argon2.low_level.hash_secret(str.encode(payload['id_card']),bytes(payload['salt'].salt.replace('"', '\''),encoding='utf8'),time_cost=1, memory_cost=8, parallelism=1, hash_len=64, type=argon2.low_level.Type.ID))[1:].replace('\'','')
            if payload['password'] != "":
                payload['password'] = str(argon2.low_level.hash_secret(str.encode(payload['password']),bcrypt.gensalt(),time_cost=1, memory_cost=8, parallelism=1, hash_len=64, type=argon2.low_level.Type.ID))[1:].replace('\'','')
            else:
                payload['password'] = None
            userobj = User(**payload)
            userobj.save()
            user = model_to_dict(userobj)
            user['role'] = userobj.role.id
            return user, 201
        api.abort(404, f"User with id card {payload['id_card']} already exist")

@check_authorization
@api.route("/card/<string:id_card>")
@api.response(404, "user not found")
@api.param("id_card", "The user card identifier")
class UserAPICard(Resource):
    """Show a single user item"""
    @login_required
    @api.doc("get_user_with_card")
    @api.marshal_with(userModel)
    def get(self, id_card):
        """Fetch a given user"""
        slist = Salt.select().order_by(Salt.year.desc())

        for s in slist:
            salt = bytes(s.salt.replace('"', '\''), encoding='utf8')
            users = User.select().where(User.salt == s.year, User.id_card == str(argon2.low_level.hash_secret(str.encode(id_card),salt,time_cost=1, memory_cost=8, parallelism=1, hash_len=64, type=argon2.low_level.Type.ID))[1:].replace('\'',''))
            for user in users:
                local_history.insert(0, user.name + " " + user.fname)
                return model_to_dict(user)
          
        local_history.insert(0, "*******")
        api.abort(404, f"User with id card {id_card} doesn't exist")

@check_authorization
@api.route("/<string:id>")
@api.response(404, "user not found")
@api.param("id", "The user  identifier")
class UserAPI(Resource):
    @login_required
    @api.doc("get_user")
    @api.marshal_with(userModel)
    def get(self, id):
        """Get a user given its identifier"""
        try:
            user = User.get(User.id==id)
        except User.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return model_to_dict(user)
    @login_required
    @api.doc("delete_user")
    @api.response(204, "User deleted")
    def delete(self, id):
        """Delete a user given its identifier"""
        try:
            User[id].delete_instance()
        except User.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return "", 204
    @login_required
    @api.expect(userModel)
    @api.marshal_with(userModel)
    def put(self, id):
        """Update a user given its identifier"""
        payload = {x: api.payload[x] for x in api.payload if x in userModel}
        if 'id' in payload:
            payload.pop('id')
        if 'id_card' in payload:
            payload.pop('id_card')
        if 'salt_year' in payload:
            payload.pop('salt_year')
        try:
           User.update(**payload).where(User.id == id).execute()
        except User.DoesNotExist:
            api.abort(404, f"User {id} doesn't exist")
        return model_to_dict(User[id])


@check_authorization
@api.route("/history")
class History(Resource):
    """Show the history of the NFC card reader. This history will reset each time you restart the app"""
    @api.doc("get_history")
    def get(self):
        """Fetch the history"""
        return local_history

@check_authorization
@api.route("/connect/<string:id_card>")
@api.response(404, "user not found")
@api.param("id_card", "The user's card identifier")
class ConnectAPI(Resource):
    @api.doc("connect_user")
    def put(self, id_card):
        """Connect a user given its identifier"""
        u = user_exsist(id_card)
        if u != False:
            login_user(u)
            return True
        api.abort(404, f"User with id {id_card} doesn't exist")



@check_authorization
@api.route("/connectpw/<string:id_card>&<string:pw>")
@api.response(404, "user not found")
@api.param("id_card", "The user's card identifier")
class ConnectPWAPI(Resource):
    @api.doc("connect_user_pw")
    def put(self, id_card, pw):
        """Connect a user given its identifier and password"""
        u = user_exsist(id_card)
        if u == False:
            api.abort(404, f"User with id {id_card} doesn't exist")
        if u.password is None:
            api.abort(404, f"User with id {id_card} can't log in with password")
        try:
            if argon2.low_level.verify_secret(str.encode(u.password),str.encode(pw),argon2.low_level.Type.ID):
                login_user(u)
                return True
        except argon2.exceptions.VerificationError:
            api.abort(404, f"Wrong password")
        


@check_authorization
@api.route("/logout")
class LogoutAPI(Resource):
    @api.doc("logout_user")
    @login_required
    def put(self):
        """Logout a user"""
        logout_user()
        return True

def user_exsist(id_card):
    "Check if an user already exist"
    slist = Salt.select().order_by(Salt.year.desc())
    for s in slist:
        salt = bytes(s.salt.replace('"', '\''), encoding='utf8')
        users = User.select().where(User.salt == s.year, User.id_card == str(argon2.low_level.hash_secret(str.encode(id_card),salt,time_cost=1, memory_cost=8, parallelism=1, hash_len=64, type=argon2.low_level.Type.ID))[1:].replace('\'',''))
        for u in users:
            return u
    return False

@login_manager.user_loader
def load_user(userid):
    return User(userid)
