#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Oder models
"""

from peewee import *

from models.user import User
from tools.db import db_wrapper

class Order(db_wrapper.Model):
    id = AutoField()
    id_manager = ForeignKeyField(User, backref="orders")
    id_client = ForeignKeyField(User, backref="orders")

class OrderDetail(db_wrapper.Model):
    id_order = ForeignKeyField(Order, backref="orderDetails")
    id_product = IntegerField()
    unit_price = IntegerField()
    quantity = IntegerField()
    class Meta:
        primary_key = CompositeKey('id_order','id_product')
