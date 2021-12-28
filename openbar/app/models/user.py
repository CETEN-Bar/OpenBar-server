#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Definition of User model and tools associated
"""

from datetime import date
from typing import Optional

import peewee as pw

from models.cardsalt import CardSalt
from models.permission import LoginType, Permission
from models.role import Role, RolePermission
from tools.crypto import verify_password, hash_card_id, verify_card_id
from tools.db import db


class User(pw.Model):
    """user object"""
    id = pw.AutoField()
    username = pw.CharField(null=True, unique=True)
    password = pw.CharField(null=True)
    first_name = pw.CharField()
    name = pw.CharField()
    role = pw.ForeignKeyField(Role, backref="users")

    card_id = pw.CharField()
    salt = pw.ForeignKeyField(CardSalt, backref="users")

    balance = pw.IntegerField(default=0)
    group_year = pw.IntegerField()
    phone = pw.CharField(null=True)
    mail = pw.CharField(null=True)
    stats_agree = pw.BooleanField(default=False)
    last_login = pw.DateTimeField(null=True)

    class Meta:
        database = db


class UserPermission(Permission):
    """Model to describe all the item in an order"""
    user_id = pw.ForeignKeyField(User,
                                 backref="permissions",
                                 on_delete='CASCADE')

    class Meta:
        database = db


def search_user(card_id: str) -> Optional[User]:
    """Return an user by its card ID"""
    salt_list = CardSalt.select().order_by(CardSalt.year.desc())
    for salt in salt_list:
        try:
            return User.get(User.salt == salt.year,
                            User.card_id == hash_card_id(card_id, salt.salt))
        except User.DoesNotExist:
            pass
    return None


def verify_user_password(user: User, password: str) -> bool:
    """Verify if the given password correspond to the User"""
    return verify_password(user.password, password)


def verify_user_card_id(user: User, card_id: str) -> bool:
    """Verify if the given card id correspond to the User"""
    if user.card_id is None:
        return False
    return verify_card_id(user.card_id, card_id)


def list_permissions(user: User, login_type: LoginType) -> list[str]:
    """List permissions of a given user"""
    def build_string(perms) -> list[str]:
        return [f"{p.permission}.{p.range}" for p in perms]

    role_perm = build_string(RolePermission.select(RolePermission.permission, RolePermission.range)
                             .where((RolePermission.role_id == user.role.id)
                                    & (RolePermission.login_type == login_type.value)))
    return role_perm + build_string(UserPermission.select(UserPermission.permission, UserPermission.range)
                                    .where((UserPermission.user_id == user.id)
                                           & (UserPermission.login_type == login_type.value)))


def update_last_login(user: User):
    """Update last login date for a given user"""
    user.last_login = str(date.today())
    user.save()
