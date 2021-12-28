#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Recharge model
"""

import datetime

import peewee as pw

from models.user import User
from tools.db import db


class Recharge(pw.Model):
    """Model to describe a recharge to an user balance"""
    id = pw.AutoField()
    barman = pw.ForeignKeyField(User, backref="recharges_made")
    client = pw.ForeignKeyField(User, backref="recharges")
    value = pw.IntegerField()
    created_at = pw.DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
