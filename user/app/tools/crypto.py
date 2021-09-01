#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of cryptographic function.
For example there are the functions to hash password and card id
"""

import os, argon2

def generate_salt():
    """Generate a random salt with the same method as argon2-cffi lib
    https://github.com/hynek/argon2-cffi/blob/58529eb865beb78a5733f059a3eb0a54e1a6718b/src/argon2/_password_hasher.py#L138
    """
    return str(os.urandom(argon2.DEFAULT_RANDOM_SALT_LENGTH))

def hashPassword(password, salt):
    "Hash the given password"

    return str(argon2.low_level.hash_secret(\
            str.encode(password),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))\
        [1:].replace('\'','')

def hashCardID(id_card, salt):
    "Hash the given Card ID"
    return str(argon2.low_level.hash_secret(\
            str.encode(id_card),
            bytes(salt, encoding='utf8'),
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=64,
            type=argon2.low_level.Type.ID))\
        [1:].replace('\'','')

def verifyHash(string, hash):
    "Verify if the given string correspond to the hash"
    try:
        if argon2.low_level.verify_secret(str.encode(string), str.encode(hash), argon2.low_level.Type.ID):
            return True
    except argon2.exceptions.VerificationError:
        pass
    return False

def verifyPassword(password, hash):
    "Verify if the given password correspond to the hash"
    return verifyHash(password, hash)

def verifyCardID(id_card, hash):
    "Verify if the given card id correspond to the hash"
    return verifyHash(id_card, hash)
