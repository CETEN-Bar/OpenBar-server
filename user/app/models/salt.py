#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the Salt model
"""

import peewee as pw
from tools.db import db_wrapper


class Salt(db_wrapper.Model):
    year = pw.IntegerField(primary_key=True)
    salt = pw.CharField()
