#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Definition of MigrationHistory model
"""

from datetime import datetime

import peewee as pw

from tools.db import db


class MigrationHistory(pw.Model):
    """
    Model to manage migration history in a database.
    The model store which migration was done to know at startup, which migration must be done.
    """
    name = pw.CharField(unique=True)
    date_applied = pw.DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db
        table_name = 'migration_history'
