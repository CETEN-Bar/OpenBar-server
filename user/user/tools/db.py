#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function initialize pony
"""

from flask import g
from pony.orm import *

db = Database()

binded = False

def initdb(app):
    "Initialise and connect to the database if necessary"
    global binded
    if not binded:
        db.bind(**app.config['PONY'])
        db.generate_mapping(create_tables=True)
        binded = True

