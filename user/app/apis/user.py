#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

import sys, os
from datetime import date
import requests


from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict
from flask_login import UserMixin, login_required, login_user, logout_user, current_user
from tools.LoginManager import login_manager

from tools.db import db_wrapper
from tools.crypto import generate_salt, hashPassword, hashCardID, verifyPassword

from apis.role import Role
from apis.salt import Salt

local_history = []

api = Namespace('user', description='User')

class UserT(UserMixin,db_wrapper.Model):
    """user object"""
    id = AutoField()
    id_card = CharField()
    name = CharField()
    fname = CharField()
    balance = IntegerField(default=0)
    role = ForeignKeyField(Role, backref="users")
    salt = ForeignKeyField(Salt, backref="users")
    group_year = IntegerField(null=True)
    username = CharField(null=True, unique=True)
    password = CharField(null=True)
    phone = CharField(null=True)
    mail = CharField(null=True)
    stats_agree = BooleanField(default=False) 
    last_login = DateTimeField()

from tools.auth import is_manager


username_login_model = api.model('Login with username', {
    'username': fields.String(
        required=True,
        description='Username'),
    'password': fields.String(
        required=True,
        description='Password'),
})

card_login_model = api.model('Login with card ID', {
    'id_card': fields.String(
        required=True,
        description='User card identifier'),
    'password': fields.String(
        required=True,
        description='Password'),
})

card_id_model = api.model('Card ID',{
    'id_card': fields.String(
        required=True,
        description='User card identifier'),
})

user_model_read = api.model('User Infos', {
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='User identifier'),
    'name': fields.String(
        required=True,
        description='User name',
        example="Sebastien"),
    'fname': fields.String(
        required=True,
        description='User first name',
        example="Da Silva"),
    'balance': fields.Integer(
        readonly=True,
        description='User balance, multiplied by 100',
        example=100),
    'role': fields.Integer(
        required=True,
        example=1,
        description='User\'s role identifier',
        attribute= lambda x: x['role'] if type(x['role']) is int else x['role']['id']),
    'group_year': fields.Integer(
        required=False,
        example=2023,
        description='User\'s group year'
    ),
    'username': fields.String(
        required=False,
        description='Username',
        example="xXx_monSeigneur54_xXx"),
    'phone': fields.String(
        required=False,
        description='Phone number',
        example="01 02 03 04 05"),
    'mail': fields.String(
        required=False,
        description='Mail',
        example="xxmonseigneurxx@telecomnancy.eu"),
    'stats_agree': fields.Boolean(
        required=True,
        description='user agreement for us to use his data for stats',
        example=False),
    'last_login': fields.Date(
        readonly=True,
        description='Date of the last login'),
})

user_model = api.clone('User', user_model_read, {
    'id_card': fields.String(
        required=True,
        description='User card identifier',
        example="04ABDC1234"),
    'password': fields.String(
        required=False,
        description='Password',
        example="BouthierUWU"),
})

@api.route("/")
class UserListAPI(Resource):
    """Shows a list of all user"""
    @is_manager(api)
    @api.doc("list_user")
    @api.marshal_list_with(user_model_read)
    def get(self):
        """List all user"""
        users = UserT.select()
        return [model_to_dict(u) for u in users]

    @api.doc("create_user")
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model_read, code=201)
    def post(self):
        """Create a new user"""
        payload = {x: api.payload[x] for x in api.payload if x in user_model}
        if 'id' in payload:
            payload.pop('id')

        try:
            payload['salt'] = Salt[date.today().year]
        except Salt.DoesNotExist:
            payload['salt'] = Salt(year=date.today().year, salt=generate_salt())
            payload['salt'].save(force_insert=True)

        if search_user(payload['id_card']):
            api.abort(409, f"User with id card {payload['id_card']} already exist")

        payload['id_card'] = hashCardID(payload['id_card'], payload['salt'].salt)
        if payload['password'] != "":
            payload['password'] = hashPassword(payload['password'], generate_salt())
        else:
            payload['password'] = None
        payload["last_login"] = str(date.today())
        userobj = UserT(**payload)
        userobj.save()
        payload["last_login"] = date.today()
        user = model_to_dict(userobj)
        user['role'] = userobj.role.id
        return user, 201

@api.route("/card/")
@api.response(404, "User not found")
class UserCardAPI(Resource):
    """Show a single user item"""
    @login_required
    @api.doc("get_user_with_card")
    @api.expect(card_id_model)
    @api.marshal_with(user_model_read)
    def get(self):
        """Fetch a given user"""
        id_card = api.payload["id_card"]

        u = search_user(id_card)
        if u != False:
            local_history.insert(0, "*******")
            api.abort(404, f"User with id card {id_card} doesn't exist")
        local_history.insert(0, u.name + " " + u.fname)
        return model_to_dict(u)

@api.route("/<string:id>")
@api.response(404, "user not found")
@api.param("id", "The user  identifier")
class UserAPI(Resource):
    @login_required
    @api.doc("get_user")
    @api.marshal_with(user_model_read)
    def get(self, id):
        """Get a user given its identifier"""
        try:
            user = UserT.get(UserT.id==id)
        except UserT.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return model_to_dict(user)

    @login_required
    @api.doc("delete_user")
    @api.response(204, "User deleted")
    def delete(self, id):
        """Delete a user given its identifier"""
        try:
            UserT[id].delete_instance()
        except UserT.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return "", 204

    @login_required
    @api.expect(user_model)
    @api.marshal_with(user_model_read)
    def put(self, id):
        """Update a user given its identifier"""
        payload = {x: api.payload[x] for x in api.payload if x in user_model}
        if 'id' in payload:
            payload.pop('id')
        if 'id_card' in payload:
            payload.pop('id_card')
        try:
           UserT.update(**payload).where(UserT.id == id).execute()
        except UserT.DoesNotExist:
            api.abort(404, f"User {id} doesn't exist")
        return model_to_dict(UserT[id])


@api.route("/history")
class History(Resource):
    """Show the history of the NFC card reader. This history will reset each time you restart the app"""
    @api.doc("get_history")
    def get(self):
        """Fetch the history"""
        return local_history

@api.route("/connect/")
@api.response(404, "User not found")
@api.param("id_card", "The user's card identifier")
class ConnectAPI(Resource):
    @api.doc("connect_user")
    @api.expect(card_id_model)
    def put(self):
        """Connect a user given its identifier"""
        id_card = api.payload['id_card']
        u = search_user(id_card)
        if u != False:
            login_user(u)
            update_ll(u)
            return True
        api.abort(404, f"User with this card id doesn't exist")



@api.route("/connectpw/")
@api.response(403, "Invalid credentials")
@api.response(404, "User not found")
class ConnectPWAPI(Resource):
    @api.doc("connect_user_password")
    @api.expect(card_login_model)
    def put(self):
        """Connect a user given its identifier and password"""
        id_card = api.payload['id_card']
        password = api.payload['password']
        u = search_user(id_card)
        if u == False:
            api.abort(404, f"User with this card doesn't exist")
        if u.password is None:
            api.abort(403, f"User with this card can't log in with password")
        if verifyPassword(u.password, password):
            login_user(u)
            update_ll(u)
            return True
        api.abort(403, "Invalid credentials")
        return False


@api.route("/logout")
class LogoutAPI(Resource):
    """Logout a user"""

    @api.doc("logout_user")
    @login_required
    def put(self):
        """Logout a user"""
        logout_user()
        return True


@api.route("/anonym/<string:id>")
@api.response(404, "user not found")
@api.param("id", "The user  identifier")
class AnonymAPI(Resource):
    @login_required
    @api.doc("anonym_user")
    @api.marshal_with(user_model_read)
    def put(self, id):
        """Anonymize a user given its identifier"""
        try:
            user = UserT[id]
            user.fname = ""
            user.name = ""
            user.mail = None
            user.phone = None 
            user.username = None
            user.group_year = None
            user.stats_agree = False

        except UserT.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return model_to_dict(user)

@login_manager.user_loader
def load_user(userid):
    "Get user by its id"
    return UserT[userid]

def search_user(id_card):
    "Return an user by its card id"
    slist = Salt.select().order_by(Salt.year.desc())
    for s in slist:
        try:
            return UserT.get(UserT.salt == s.year, UserT.id_card == hashCardID(id_card, s.salt))
        except UserT.DoesNotExist:
            pass
    return False

def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([Salt, UserT])

def update_ll(u):
    "Update last login date for a given user"
    u.last_login = str(date.today())
    u.save()
