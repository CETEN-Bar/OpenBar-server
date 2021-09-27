#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Recharge model
"""

from peewee import *

from models.user import User
from tools.db import db_wrapper

class Recharge(db_wrapper.Model):
    id = IntegerField()
    id_manager= ForeignKeyField(User, backref="recharges")
    id_user_client = ForeignKeyField(User, backref="recharges")
    value = IntegerField()
    date = DateTimeField()
