#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialisation of models
"""
from models.cardsalt import CardSalt
from models.order import Order, OrderProduct
from models.permission import Permission
from models.recharge import Recharge
from models.role import Role, RolePermission
from models.user import User, UserPermission
from tools.db import db


def create_tables():
    """Create tables for all models"""
    db.create_tables([User, Role, CardSalt, Recharge, Order,
                      OrderProduct, Permission, RolePermission,
                      UserPermission])
