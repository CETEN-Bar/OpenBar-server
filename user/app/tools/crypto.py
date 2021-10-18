#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of cryptographic function.
For example there are the functions to hash password and card id
"""

import os
from datetime import datetime, timedelta
import argon2
import jwt

ISSUER_NAME = "OpenBar Auth"


def generate_salt():
    """Generate a random salt with the same method as argon2-cffi lib
    https://github.com/hynek/argon2-cffi/blob/58529eb865beb78a5733f059a3eb0a54e1a6718b/src/argon2/_password_hasher.py#L138
    """
    return str(os.urandom(argon2.DEFAULT_RANDOM_SALT_LENGTH))


def hash_password(password, salt):
    "Hash the given password"

    return str(argon2.low_level.hash_secret(
            str.encode(password),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))[1:] \
        .replace('\'', '')


def hash_cardID(id_card, salt):
    "Hash the given Card ID"
    return str(argon2.low_level.hash_secret(
            str.encode(id_card),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))[1:] \
        .replace('\'', '')


def verify_hash(hashstring, string):
    "Verify if the given string correspond to the hash"
    try:
        if argon2.low_level.verify_secret(str.encode(hashstring), str.encode(string),
                                          argon2.low_level.Type.ID):
            return True
    except argon2.exceptions.VerificationError:
        pass
    return False


def verify_password(hashstring, password):
    "Verify if the given password correspond to the hash"
    return verify_hash(hashstring, password)


def verify_cardID(hashstring, id_card):
    "Verify if the given card id correspond to the hash"
    return verify_hash(hashstring, id_card)


def generate_user_token(user_id, permissions):
    "Return an auth token given"
    return jwt.encode(
        {"exp": datetime.utcnow() + timedelta(seconds=3000),
         "nbf": datetime.utcnow(),
         "iss": ISSUER_NAME,
         "aud": permissions,
         "sub": user_id},
        "secret", algorithm="HS512"
    )


def decode_user_token(encoded, fail_function, availible_audience):
    """Decode a encoded JWT
    If an error occurs fail_function(code, message) will be called
    availible_audience is a list of sring describing allowed audience
    """
    try:
        return jwt.decode(encoded, "secret",
                          algorithms=["HS512"],
                          issuer=ISSUER_NAME,
                          audience=availible_audience,
                          options={"require":
                                   ["exp", "nbf", "iss", "aud", "sub"]},)
    except jwt.ExpiredSignatureError:
        fail_function(401, "Token expired")
    except (jwt.InvalidIssuedAtError, jwt.ImmatureSignatureError):
        fail_function(401, "Token not yet valid")
    except (jwt.InvalidAudienceError, jwt.InvalidIssuerError,
            jwt.InvalidKeyError, jwt.InvalidAlgorithmError,
            jwt.MissingRequiredClaimError):
        fail_function(401, "Invalid token")
    except jwt.InvalidSignatureError:
        fail_function(401, "Invalid Signature")
    except (jwt.InvalidTokenError, jwt.DecodeError):
        fail_function(400, "Bad token")
