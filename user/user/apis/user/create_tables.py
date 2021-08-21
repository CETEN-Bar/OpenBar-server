#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File for the create_tables method
"""

from tools.db import db_wrapper

from .user import User

def create_tables():
    "Create tables for the namespace"
    db_wrapper.database.create_tables([User])
