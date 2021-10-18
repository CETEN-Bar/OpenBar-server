#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Role model
"""

import peewee as pw
from tools.db import db_wrapper


class Role(db_wrapper.Model):
    "DAO of a user role"
    id = pw.AutoField()
    lib = pw.CharField()
    is_admin = pw.BooleanField(default=False)
    is_barman = pw.BooleanField(default=False)
