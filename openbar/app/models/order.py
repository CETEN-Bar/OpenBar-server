#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Oder models
"""
import datetime
from enum import Enum

import peewee as pw
from fastapi import HTTPException
from starlette import status

from models.user import User
from tools.db import db


class OrderStatus(Enum):
    """
    Describe the state of an order
    """
    IN_BASKET = 0
    VALIDATED = 1
    FINISHED = 2
    CANCELLED = 3


class Order(pw.Model):
    """Model to describe an order"""
    id = pw.AutoField()
    client = pw.ForeignKeyField(User, backref="orders")
    barman = pw.ForeignKeyField(User, backref="orders_served", null=True)
    status = pw.IntegerField(default=OrderStatus.IN_BASKET.value)
    created_at = pw.DateTimeField(default=datetime.datetime.now)
    validated_at = pw.DateTimeField(null=True)
    ended_at = pw.DateTimeField(null=True)

    class Meta:
        database = db


class OrderProduct(pw.Model):
    """Model to describe all the item in an order"""
    order = pw.ForeignKeyField(Order,
                               backref="products",
                               on_delete='CASCADE')
    product = pw.IntegerField()
    unit_price = pw.IntegerField()
    quantity = pw.IntegerField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey('order', 'product')


def calculate_total(order: Order) -> int:
    """
    Return the total price of an order
    :param order: current order
    :return: Total price
    """
    return order.products\
        .select(pw.fn.SUM(OrderProduct.unit_price * OrderProduct.quantity))\
        .scalar()


def validate_order(order: Order) -> None:
    """
    Validate the order
    :param order: order to be validated
    """
    # TODO: check product availability and price + update storage
    total = calculate_total(order)
    if order.client.balance < total:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="User doesn't have enough money to validate the order. Please update the order.")
    order.client.balance -= total
    order.client.save()
    order.status = OrderStatus.VALIDATED.value
    order.validated_at = datetime.datetime.now()
    order.save()


def cancel_order_by(order: Order, barman: User) -> None:
    """
    Cancel the order
    :param order: order to be cancelled
    :param barman: user cancelling the order
    """
    # TODO: update storage
    total = calculate_total(order)
    order.client.balance += total
    order.client.save()
    order.status = OrderStatus.CANCELLED.value
    order.ended_at = datetime.datetime.now()
    order.barman = barman
    order.save()


def finish_the_order(order: Order, barman: User) -> None:
    """
    Finish the order
    This means that the
    :param order: order to be finished
    :param barman: user cancelling the order
    """
    order.status = OrderStatus.FINISHED.value
    order.ended_at = datetime.datetime.now()
    order.barman = barman
    order.save()
