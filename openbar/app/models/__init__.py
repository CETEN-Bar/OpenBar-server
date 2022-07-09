#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialisation of models
"""


def create_tables():
    """Create tables for all models"""
    from models.migration.MigrationHistory import MigrationHistory
    from models.cardsalt import CardSalt
    from models.order import Order, OrderProduct
    from models.permission import Permission
    from models.recharge import Recharge
    from models.role import Role, RolePermission
    from models.user import User, UserPermission
    from tools.db import db
    db.create_tables([User, Role, CardSalt, Recharge, Order,
                      OrderProduct, Permission, RolePermission,
                      UserPermission, MigrationHistory])
