#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialize the socketio variable
"""


from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")