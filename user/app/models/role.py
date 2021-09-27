#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Role model
"""

from peewee import *

from tools.db import db_wrapper

class Role(db_wrapper.Model):
    "DAO of a user role"
    id = AutoField()
    lib = CharField()
    is_admin = BooleanField(default=False)
    is_barman = BooleanField(default=False)
