#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Migration of database
"""

from playhouse.reflection import generate_models

from tools.db import db


def migrate():
    """Migrate to the latest version of the database"""
    from models.migration.MigrationHistory import MigrationHistory

    __all_migrations__ = []

    models = generate_models(db)
    keys = models.keys()

    if 'user' not in keys:
        # We suppose the database is empty
        from models import create_tables
        create_tables()
        for name, _ in __all_migrations__:
            MigrationHistory.create(name=name)
        return
    if 'migration_history' not in keys:
        db.create_tables([MigrationHistory])
    for name, migrate_fn in __all_migrations__:
        if MigrationHistory.get_or_none(name=name) is not None:
            continue
        migrate_fn()
        MigrationHistory.create(name=name)
