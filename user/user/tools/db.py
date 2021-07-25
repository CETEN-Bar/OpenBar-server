#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function initialize sqlalchemy
"""

from flask import g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_session():
    """Return the session of the db
    and initialize  the db if necessery
    """
    if getattr(g, '_db_init', None) == None:
        db.create_all()
        g._db_init = True
    return db.session
