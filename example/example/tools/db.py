#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to manage the database
"""

from pony.orm import Database

db = Database()
binded = False

def initdb(app):
    "Initialise and connect to the database if necessary"
    global binded
    if not binded:
        db.bind(**app.config['PONY'])
        db.generate_mapping(create_tables=True)
        binded = True
