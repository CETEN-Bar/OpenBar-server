#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to manage the database
"""

import os
from contextvars import ContextVar

import peewee
from fastapi import Depends
from playhouse.db_url import connect

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state_current = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state_current)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = None
db_uri = os.environ.get('DATABASE', default="sqlite:////tmp/db")
is_sqlite = db_uri.startswith("sqlite:")

if is_sqlite:
    db = connect(db_uri, check_same_thread=False)
else:
    db = connect(db_uri)

db._state = PeeweeConnectionState()


async def reset_db_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        db.connect()
        yield
    finally:
        if not db.is_closed():
            db.close()
