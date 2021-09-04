#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict
from datetime import date
import logging

from tools.db import db_wrapper
from apis.user import UserT
from flask_login import login_required, current_user
from tools.LoginManager import login_manager
from tools.auth import is_manager

log = logging.getLogger(__name__)

api = Namespace('order', description='order')

class Order(db_wrapper.Model):
    id = AutoField()
    id_manager = ForeignKeyField(UserT,backref="orde")
    id_client = ForeignKeyField(UserT,backref="orde")

class OrderDetail(db_wrapper.Model):
    id_order = ForeignKeyField(Order,backref="orderd")
    id_product = IntegerField()
    unit_price = IntegerField()
    quantity = IntegerField()
    class Meta:
        primary_key = CompositeKey('id_order','id_product')



items = api.model('Item list', {
    'id_product': fields.Integer,
    'quantity': fields.String,
})

orderlist_complete = api.clone('Order list', items ,{
    'quantity': fields.Integer,
})

orderBaseModel = api.model('Order', {
    'id': fields.Integer(
        readonly=True,
        description='Order id'),
    'id_manager': fields.Integer(
        required=True,
        description='Id of the admin who managed the order',
        attribute= lambda x: x['id_manager'] if type(x['id_manager']) is int else x['id_manager']['id']),
    'id_client': fields.Integer(
        required=True,
        description='Id of the client',
        attribute= lambda x: x['id_client'] if type(x['id_client']) is int else x['id_client']['id']),})

orderModel = api.clone('Order Model',orderBaseModel, {
    'item_list': fields.List(fields.Nested(items)),
})

orderModelRead = api.clone('Order Read', orderBaseModel, {
    'item_list': fields.List(fields.Nested(orderlist_complete)),
})


@api.route("/")
class OrderAPI(Resource):
    @api.doc("new_order")
    @is_manager(api)
    @api.expect(orderModel, validate=True)
    @api.marshal_with(orderModel, code=201)
    def post(self):
        payload = {x: api.payload[x] for x in api.payload if x in orderModel}
        payload['id'] = len(Order)+1
        payload_order = {"id":payload['id'],"id_manager" : payload["id_manager"] , "id_client" : payload["id_client"]}
        order = Order(**payload_order)
        order.save(force_insert=True)
        for item in payload["item_list"]:
            item["id_order"] = payload['id']
            item["quantity"] = 1
            item["unit_price"] = 1
            x = OrderDetail(**item)
            x.save(force_insert=True)
        return payload, 201

@api.route("/<string:id>")
@api.param("id", "The order  identifier")
class OrderIDAPI(Resource):
    @api.doc("get_order")
    @is_manager(api)
    @api.marshal_with(orderModelRead, code=201)
    def get(self,id):
        order = Order[id]
        x = []
        for item in OrderDetail.select().where(OrderDetail.id_order==id):
            x.append(model_to_dict(item))
        
        to_ret = model_to_dict(order)
        to_ret["item_list"] = x
        return to_ret

    
    

def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([Order,OrderDetail])