#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Definition of User model and tools associated
"""

from datetime import date
import peewee as pw

from models.role import Role
from models.salt import Salt
from tools.db import db_wrapper
from tools.crypto import verify_password, hash_cardID, verify_cardID


class User(db_wrapper.Model):
    """user object"""
    id = pw.AutoField()
    id_card = pw.CharField()
    name = pw.CharField()
    fname = pw.CharField()
    balance = pw.IntegerField(default=0)
    role = pw.ForeignKeyField(Role, backref="users")
    salt = pw.ForeignKeyField(Salt, backref="users")
    group_year = pw.IntegerField(null=True)
    username = pw.CharField(null=True, unique=True)
    password = pw.CharField(null=True)
    phone = pw.CharField(null=True)
    mail = pw.CharField(null=True)
    stats_agree = pw.BooleanField(default=False)
    last_login = pw.DateTimeField()


def search_user(id_card):
    "Return an user by its card id"
    salt_list = Salt.select().order_by(Salt.year.desc())
    for salt in salt_list:
        try:
            return User.get(User.salt == salt.year,
                            User.id_card == hash_cardID(id_card, salt.salt))
        except User.DoesNotExist:
            pass
    return False


def verify_user_password(user, password):
    "Verify if the given password correspond to the User"
    return verify_password(user.password, password)


def verify_user_cardID(user, id_card):
    "Verify if the given card id correspond to the User"
    if user.id_card is None:
        return False
    return verify_cardID(user.id_card, id_card)


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
