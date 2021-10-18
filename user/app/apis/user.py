#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API of User managment
"""

from datetime import date

from flask_restx import Namespace, Resource, fields
from playhouse.shortcuts import model_to_dict

from tools.crypto import generate_salt, hash_password, hash_cardID
from tools.auth import is_password_logged, is_token_logged, is_barman,\
    is_fully_logged

from models.user import User as UserDAO, search_user
from models.salt import Salt

api = Namespace('user', description='User')

card_id_model = api.model('Card ID', {
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
        attribute=lambda x: x['role']
                    if isinstance(x['role'], int) else x['role']['id']),
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
class UserList(Resource):
    """Shows a list of all user"""
    @api.doc("list_user", security='token')
    @api.marshal_list_with(user_model_read)
    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    def get(self):
        """List all user"""
        users = UserDAO.select()
        return [model_to_dict(u) for u in users]

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("create_user", security='password')
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
            payload['salt'] = Salt(year=date.today().year,
                                   salt=generate_salt())
            payload['salt'].save(force_insert=True)

        if search_user(payload['id_card']):
            api.abort(409,
                      "User with id card {payload['id_card']} already exist")

        payload['id_card'] = hash_cardID(payload['id_card'],
                                        payload['salt'].salt)
        if payload['password'] != "":
            payload['password'] = hash_password(payload['password'],
                                               generate_salt())
        else:
            payload['password'] = None
        payload["last_login"] = str(date.today())
        userobj = UserDAO(**payload)
        userobj.save()
        payload["last_login"] = date.today()
        user = model_to_dict(userobj)
        user['role'] = userobj.role.id
        return user, 201


@api.route("/card/")
@api.response(404, "User not found")
class UserCardAPI(Resource):
    """Show a single user item"""
    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    @api.doc("get_user_with_card", security='token')
    @api.expect(card_id_model)
    @api.marshal_with(user_model_read)
    def get(self):
        """Fetch a given user"""
        id_card = api.payload["id_card"]

        user = search_user(id_card)
        if user is not False:
            api.abort(404, f"User with id card {id_card} doesn't exist")
        return model_to_dict(user)


@api.route("/<string:id>")
@api.response(404, "user not found")
@api.param("id", "The user  identifier")
class User(Resource):
    """API to manage an user"""
    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    @api.doc("get_user", security='token')
    @api.marshal_with(user_model_read)
    def get(self, id):
        """Get a user given its identifier"""
        try:
            user = UserDAO.get(UserDAO.id == id)
        except UserDAO.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return model_to_dict(user)

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("delete_user", security='password')
    @api.response(204, "User deleted")
    def delete(self, id):
        """Delete a user given its identifier"""
        try:
            User[id].delete_instance()
        except UserDAO.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return "", 204

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("put_user", security='password')
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
            UserDAO.update(**payload).where(UserDAO.id == id).execute()
        except UserDAO.DoesNotExist:
            api.abort(404, f"User {id} doesn't exist")
        return model_to_dict(User[id])


@api.route("/anonym/<string:id>")
@api.response(404, "user not found")
@api.param("id", "The user  identifier")
class Anonymise(Resource):
    "API to anonymise users to be GDPR compliant"
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("anonym_user", security='password')
    @api.marshal_with(user_model_read)
    def put(self, id):
        """Anonymize a user given its identifier"""
        try:
            user = User[id]
            user.fname = ""
            user.name = ""
            user.mail = None
            user.phone = None
            user.username = None
            user.group_year = None
            user.stats_agree = False

        except UserDAO.DoesNotExist:
            api.abort(404, f"User with id {id} doesn't exist")
        return model_to_dict(user)
