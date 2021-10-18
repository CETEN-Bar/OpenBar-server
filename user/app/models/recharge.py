#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Recharge model
"""

import peewee as pw

from models.user import User
from tools.db import db_wrapper


class Recharge(db_wrapper.Model):
    """Model to describe a recharge to an user balance"""
    id = pw.IntegerField()
    id_manager = pw.ForeignKeyField(User, backref="recharges")
    id_user_client = pw.ForeignKeyField(User, backref="recharges")
    value = pw.IntegerField()
    date = pw.DateTimeField()
