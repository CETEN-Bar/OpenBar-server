#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialisation of models
"""

from tools.db import db_wrapper

from models.order import Order, OrderDetail, OrderStatus
from models.recharge import Recharge
from models.role import Role
from models.salt import Salt
from models.user import User

def create_tables():
    "Create tables for all models"
    db_wrapper.database.create_tables([User, Role, Salt, Recharge, Order, OrderDetail, OrderStatus])
