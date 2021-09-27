#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the Salt model
"""

from peewee import *
from tools.db import db_wrapper

class Salt(db_wrapper.Model):
    year = IntegerField(primary_key=True)
    salt = CharField()
