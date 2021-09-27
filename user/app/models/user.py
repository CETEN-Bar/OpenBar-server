#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Definition of User model and tools associated
"""

from datetime import date
from peewee import *

from models.role import Role
from models.salt import Salt
from tools.db import db_wrapper
from tools.crypto import verifyPassword, hashCardID, verifyCardID

class User(db_wrapper.Model):
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

def search_user(id_card):
    "Return an user by its card id"
    slist = Salt.select().order_by(Salt.year.desc())
    for s in slist:
        try:
            return User.get(User.salt == s.year, User.id_card == hashCardID(id_card, s.salt))
        except User.DoesNotExist:
            pass
    return False

def verifyUserPassword(user, password):
    "Verify if the given password correspond to the User"
    return verifyPassword(user.password, password)

def verifyUserCardID(user, id_card):
    "Verify if the given card id correspond to the User"
    if user.id_card is None:
        return False
    return verifyCardID(user.id_card, id_card)

def list_permissions(user):
    "List permissions of a given user"
    permissions = []
    if user.role.is_admin:
        permissions.append("admin")
    if user.role.is_barman:
        permissions.append("barman")
    return permissions

def update_last_login(user):
    "Update last login date for a given user"
    user.last_login = str(date.today())
    user.save()
