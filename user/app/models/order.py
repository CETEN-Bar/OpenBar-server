#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Oder models
"""

from enum import Enum
from peewee import *

from models.user import User
from tools.db import db_wrapper

class StatusEnum(Enum):
    INBASKET = 1
    VALIDATED = 2
    FINISHED = 3
    CANCELED = 4

class OrderStatus(db_wrapper.Model):
    id = AutoField()
    lib = CharField()

class Order(db_wrapper.Model):
    id = AutoField()
    id_manager = ForeignKeyField(User, backref="orders", null=True)
    id_client = ForeignKeyField(User, backref="orders")
    id_status = ForeignKeyField(OrderStatus, backref="orders")

class OrderDetail(db_wrapper.Model):
    id_order = ForeignKeyField(Order, backref="orderDetails", on_delete='CASCADE')
    id_product = IntegerField()
    unit_price = IntegerField()
    quantity = IntegerField()
    class Meta:
        primary_key = CompositeKey('id_order', 'id_product')
