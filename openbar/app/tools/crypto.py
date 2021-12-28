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
from fastapi import HTTPException
from starlette import status

from config import ISSUER_NAME, TOKEN_VALIDITY_TIME


def generate_salt():
    """Generate a random salt with the same method as argon2-cffi lib
    https://github.com/hynek/argon2-cffi/blob/58529eb865beb78a5733f059a3eb0a54e1a6718b/src/argon2/_password_hasher.py#L138
    """
    return str(os.urandom(argon2.DEFAULT_RANDOM_SALT_LENGTH))


def hash_password(password, salt):
    """Hash the given password"""

    return str(argon2.low_level.hash_secret(
            str.encode(password),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))[1:] \
        .replace('\'', '')


def hash_card_id(card_id, salt):
    """Hash the given Card ID"""
    return str(argon2.low_level.hash_secret(
            str.encode(card_id),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))[1:] \
        .replace('\'', '')


def verify_hash(hash_string, string):
    """Verify if the given string correspond to the hash"""
    try:
        if argon2.low_level.verify_secret(str.encode(hash_string), str.encode(string),
                                          argon2.low_level.Type.ID):
            return True
    except argon2.exceptions.VerificationError:
        pass
    return False


def verify_password(hash_string, password):
    """Verify if the given password correspond to the hash"""
    return verify_hash(hash_string, password)


def verify_card_id(hash_string, card_id):
    """Verify if the given card id correspond to the hash"""
    return verify_hash(hash_string, card_id)


def generate_user_token(user_id, permissions):
    """Return an auth token given"""
    # TODO : sign with asymmetric keys
    return jwt.encode(
        {"exp": datetime.utcnow() + timedelta(seconds=TOKEN_VALIDITY_TIME),
         "nbf": datetime.utcnow(),
         "iss": ISSUER_NAME,
         "aud": permissions,
         "sub": user_id},
        "secret", algorithm="HS512"
    )


def decode_user_token(encoded):
    """Decode a encoded JWT
    If an error occurs fail_function(code, message) will be called
    available_audience is a list of string describing allowed audience
    """
    try:
        return jwt.decode(encoded, "secret",
                          algorithms=["HS512"],
                          issuer=ISSUER_NAME,
                          options={"require":
                                   ["exp", "nbf", "iss", "aud", "sub"]}, )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidIssuedAtError, jwt.ImmatureSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not yet valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidAudienceError, jwt.InvalidIssuerError,
            jwt.InvalidKeyError, jwt.InvalidAlgorithmError,
            jwt.MissingRequiredClaimError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
