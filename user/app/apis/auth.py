#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for authentification
"""

from flask_restx import Namespace, Resource, fields

from models.user import User, search_user, verify_user_password, \
    update_last_login
from tools.auth import login_user, is_token_logged, is_barman

api = Namespace('auth', description='Authentification API')

local_history = []

login_model = api.model('Login', {
    'username': fields.String(
        required=False,
        description='Username'),
    'id_card': fields.String(
        required=False,
        description='User card identifier'),
    'password': fields.String(
        required=False,
        description='Password'),
})


@api.route("/login")
@api.response(400, "Invalid request")
@api.response(401, "Invalid credentials")
class Login(Resource):
    """API for authentification"""
    @api.doc("connect_user")
    @api.expect(login_model)
    def put(self):
        """Login an user using its identifier
        id_card only : fast login, only allow ordering
        id_card with password or username with password : full login
        """
        full_login = 'password' in api.payload
        user = None
        if full_login and 'username' in api.payload:
            try:
                user = User.get(User.username == api.payload['username'])
            except User.DoesNotExist:
                api.abort(401, "Invalid credentials")
        if user is None and 'id_card' in api.payload:
            id_card = api.payload['id_card']
            user = search_user(id_card)
        if user is None:
            api.abort(400, "Invalid request. No identifier given")
        if user is False:
            local_history.append(None)
            api.abort(401, "Invalid credentials")
        local_history.append(user.id)

        if (full_login
                and not verify_user_password(user, api.payload['password'])):
            api.abort(401, "Invalid credentials")

        # User is now authentificated, we can proceed
        update_last_login(user)
        return login_user(user, full_login)


@api.route("/history")
class History(Resource):
    """Show the history of the logins by a card id.
    This history will reset each time you restart the app.
    """
    @is_token_logged(api)
    @is_barman(api)
    @api.doc("get_history", security='token')
    def get(self):
        """Fetch the history"""
        return local_history
