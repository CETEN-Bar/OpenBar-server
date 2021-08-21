#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core initialisation of the user namespace
"""

from flask_restx import Namespace

api = Namespace('user', description='User')
