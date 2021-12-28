#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base definition of a permission
"""
from enum import Enum

import peewee as pw

from tools.db import db


class LoginType(Enum):
    """
    Describe how the user logged in as some method are less secure than other.
    PARTIAL_LOGIN : corresponds to a login with just a nfc card.
    NORMAL_LOGIN : is a login with a password.
    And PASSWORD : is when the user made a onetime password confirmation
    Please see apis/auth.py for more details.
    """
    PARTIAL_LOGIN = 0
    NORMAL_LOGIN = 1
    PASSWORD = 2


class Range(Enum):
    """
    Describe what range of ressource owner the user can access.
    SELF : if the current user own the ressource
    UNDERPRIVILEGED : if the role of the owner if a subrole of the role of the actual user
    EVERYONE : every ressources
    """
    SELF = 0
    UNDERPRIVILEGED = 1
    EVERYONE = 2


class Permission(pw.Model):
    """
    Model to describe what the base permission should looks like.
    Then a permission can be given to a specific user or role.
    """
    id = pw.AutoField()
    permission = pw.CharField()
    login_type = pw.IntegerField()
    range = pw.IntegerField()

    class Meta:
        database = db
