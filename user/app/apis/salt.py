#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

import sys

from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict

from tools.db import db_wrapper

class Salt(db_wrapper.Model):
    year = IntegerField(primary_key=True)
    salt = CharField()
