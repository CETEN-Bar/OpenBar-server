#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to check authorization before accessing the API.
"""

from functools import wraps

from flask import g, request
from werkzeug.http import parse_authorization_header

from models.user import User, verify_user_password, list_permissions
from tools.crypto import generate_user_token, decode_user_token

WWW_AUTH_TOKEN_HEADER = 'Bearer'
WWW_AUTH_HEADER_PASSWORD = 'Basic realm="Barman modification"'

PERMISSION_BARMAN_MODIFICATION = "barman_modification"
PERMISSION_FULL_LOGIN = "full_login"

authorizations = {
    'token': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    },
    'password': {
        'type': 'basic'
    }
}


def login_user(user, full_login=False):
    """Return a token for a user."""
    permissions = list_permissions(user)
    if full_login:
        permissions.append(PERMISSION_FULL_LOGIN)
    return generate_user_token(user.id, permissions)


class TokenAuthError(Exception):
    """Exception if token auth failed."""
    def __init__(self, message, code):
        super(TokenAuthError, self).__init__(message)
        self.message = message
        self.code = code


class PasswordAuthError(Exception):
    """Exception if password auth failed."""
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message
        self.code = code


def fail_token_function(code, msg):
    """Wrapper for raising an error
    in case of a failed token authentification.
    """
    raise TokenAuthError(msg, code)


def fail_password_function(code, msg):
    """Wrapper for raising an error
    in case of a failed password authentification.
    """
    raise PasswordAuthError(msg, code)


def is_password_logged(api):
    """Deccorator to allow a route only
    if the user has just given it's password with a HTTP Basic Auth header.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.headers.get('Authorization'):
                fail_password_function(401, "Authorization header is required")
            credentails = parse_authorization_header(
                request.headers.get('Authorization'))
            if not credentails:
                fail_password_function(400, "Authorization header isn't valid")
            if credentails.username is None or credentails.password is None:
                fail_password_function(400, "Authorization header isn't valid")
            try:
                user = User.get(User.username == credentails.username)
            except User.DoesNotExist:
                fail_password_function(401, "Authorization header isn't valid")
            if not verify_user_password(user, credentails.password):
                fail_password_function(401, "Authorization header isn't valid")
            permissions = list_permissions(user)
            permissions.append(PERMISSION_BARMAN_MODIFICATION)
            permissions.append(PERMISSION_FULL_LOGIN)
            g.current_user = user.id
            g.user_permissions = permissions
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def is_token_logged(api):
    """Deccorator to restrict a route to a logged user with token."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            header = request.headers.get('Authorization')
            if not header:
                fail_token_function(401, "Authorization header is required")
            splitted = header.split()
            if len(splitted) != 2 or splitted[0] != "Bearer":
                fail_token_function(400, "Authorization header isn't valid")
            token = decode_user_token(splitted[1], fail_token_function,
                                      [PERMISSION_FULL_LOGIN,
                                       "admin", "barman"])
            user_id = None
            try:
                user_id = int(token['sub'])
            except ValueError:
                fail_token_function(401, "Invalid token")
            try:
                User.get(User.id == user_id)
            except User.DoesNotExist:
                fail_token_function(401, "The user doesn't exist anymore")

            if (not isinstance(token['aud'], list)
                    or any(not isinstance(x, str) for x in token['aud'])):
                fail_token_function(401, "Invalid token")
                g.current_user = user_id
            g.user_permissions = token['aud']
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def is_barman(api):
    """Deccorator to restrict a route to barman.
    An authentification method should already have been checked
    (with is_token_logged for example).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permissions = g.get("user_permissions", None)
            assert permissions is not None
            if "barman" not in permissions:
                api.abort(401, "Unauthorized")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def is_admin(api):
    """Deccorator to restrict a route to logged user.
    An authentification method should already have been checked
    (with is_token_logged for example).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permissions = g.get("user_permissions", None)
            assert permissions is not None
            if "admin" not in permissions:
                api.abort(401, "Unauthorized")
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def is_fully_logged(api):
    """Deccorator to a fully logged user.
    An authentification method should already have been checked
    (with is_token_logged for example).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permissions = g.get("user_permissions", None)
            assert permissions is not None
            if PERMISSION_FULL_LOGIN not in permissions:
                api.abort(401, "Unauthorized")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
