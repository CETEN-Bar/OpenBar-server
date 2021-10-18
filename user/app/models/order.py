#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Oder models
"""

from enum import Enum
import peewee as pw

from models.user import User
from tools.db import db_wrapper


class StatusEnum(Enum):
    """Enum to describe the status of an order"""
    INBASKET = 1
    VALIDATED = 2
    FINISHED = 3
    CANCELED = 4


class OrderStatus(db_wrapper.Model):
    """Model describing order status"""
    id = pw.AutoField()
    lib = pw.CharField()


class Order(db_wrapper.Model):
    """Model to describe an order"""
    id = pw.AutoField()
    id_barman = pw.ForeignKeyField(User, backref="orders_served", null=True)
    id_client = pw.ForeignKeyField(User, backref="orders")
    id_status = pw.ForeignKeyField(OrderStatus, backref="orders")


class OrderDetail(db_wrapper.Model):
    """Model to describe all the item in an order"""
    id_order = pw.ForeignKeyField(Order,
                                  backref="orderDetails",
                                  on_delete='CASCADE')
    id_product = pw.IntegerField()
    unit_price = pw.IntegerField()
    quantity = pw.IntegerField()

    class Meta:
        primary_key = pw.CompositeKey('id_order', 'id_product')
