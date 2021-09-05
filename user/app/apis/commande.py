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
from enum import Enum

from tools.db import db_wrapper
from apis.user import UserT
from flask_login import login_required, current_user
from tools.LoginManager import login_manager
from tools.auth import is_manager

log = logging.getLogger(__name__)

api = Namespace('order', description='order')

class Status(Enum):
    INBASKET = 1
    VALIDATED = 2
    FINISHED = 3
    CANCELED = 4


class Stats(db_wrapper.Model):
    id = AutoField()
    lib = CharField()



class Order(db_wrapper.Model):
    id = AutoField()
    id_manager = ForeignKeyField(UserT,backref="orde",null=True)
    id_client = ForeignKeyField(UserT,backref="orde")
    id_status = ForeignKeyField(Stats,backref="orde")

class OrderDetail(db_wrapper.Model):
    id_order = ForeignKeyField(Order,backref="orderd",on_delete='CASCADE')
    id_product = IntegerField()
    unit_price = IntegerField()
    quantity = IntegerField()
    class Meta:
        primary_key = CompositeKey('id_order','id_product')



itemsBase = api.model('Item Base', {
    'id_order' : fields.Integer(
        attribute= lambda x: x['id_order'] if type(x['id_order']) is int else x['id_order']['id']),
    'id_product': fields.Integer,
})

items = api.clone('Item list', itemsBase, {
    'quantity': fields.Integer,
})

orderlist_complete = api.clone('Order list', items ,{
    'unit_price': fields.Integer,
})

orderID = api.model('Order ID', {
    'id': fields.Integer(
        description='Order id'),
})

orderValidate = api.clone('Order Validate', orderID,{
    'id_manager': fields.Integer(
        description='Manager id'),
})

orderBaseModel = api.model("Order", {
    'id': fields.Integer(
        readonly=True,
        description='Order id'),
    'id_client': fields.Integer(
        required=True,
        description='Id of the client',
        attribute= lambda x: x['id_client'] if type(x['id_client']) is int else x['id_client']['id']),
    'id_status': fields.Integer(
        readonly=True,
        description='Order status',
        attribute= lambda x: x['id_status'] if type(x['id_status']) is int else x['id_status']['id']),
})

orderModel = api.clone('Order Model',orderBaseModel, {
    'item_list': fields.List(fields.Nested(items)),
})

orderModelRead = api.clone('Order Read', orderBaseModel, {
    'id_manager': fields.Integer(
        required=True,
        description='Id of the admin who managed the order',
        attribute= lambda x: x['id_manager'] if type(x['id_manager']) is int else x['id_manager']['id']),
    'item_list': fields.List(fields.Nested(orderlist_complete)),
})


orderFinishModel =  api.model("Order Finish model", {
    'id': fields.Integer(
        description='Order id'),
    'id_manager': fields.Integer(
        required=True,
        description='Id of the admin who managed the order'),
})
        

@api.route("/")
class OrderAPI(Resource):
    @api.doc("new_order")
    @is_manager(api)
    @api.expect(orderBaseModel, validate=True)
    @api.marshal_with(orderBaseModel, code=201)
    def post(self):
        """Create a new order in progress"""
        payload = {x: api.payload[x] for x in api.payload if x in orderBaseModel}
        payload['id_status'] = Status.INBASKET.value
        if 'id' in payload:
            payload.pop('id')
        order = Order(**payload)
        order.save(force_insert=True)
        return model_to_dict(order), 201

    @api.doc("validate_basket")
    @api.expect(orderID,validate=True)
    @api.marshal_with(orderBaseModel, code=201)
    def put(self):
        """Validation of the basket"""
        payload = {x: api.payload[x] for x in api.payload if x in orderID}
        orderD = OrderDetail.select().where(OrderDetail.id_order==payload['id'])
        orderQ = Order[payload['id']]
        if orderQ.id_status.id == Status.INBASKET.value:
            tot = 0
            for i in orderD:
                tot += i.unit_price * i.quantity * 100
            if UserT[orderQ.id_client].balance >= tot:
                Order.update({Order.id_status : Status.VALIDATED.value}).where(Order.id == payload['id']).execute()
                res = UserT[orderQ.id_client].balance - tot
                UserT.update({UserT.balance : res}).where(UserT.id == orderQ.id_client).execute()
                return model_to_dict(Order[payload['id']]), 201
            api.abort(404, f"Not enought money")
        api.abort(404, f"Basket already validated")



@api.route("/cancel")
class OrderAPICancem(Resource):
    @api.doc("cancel_order")
    @api.expect(orderID,validate=True)
    def put(self):
        """Cancel order and give money back if necessary"""
        try:
            payload = {x: api.payload[x] for x in api.payload if x in orderID}
            orderD = OrderDetail.select().where(OrderDetail.id_order==payload['id'])
            orderQ = Order[payload['id']]
            if orderQ.id_status.id != Status.FINISHED.value:
                if orderQ.id_status.id == Status.VALIDATED.value:
                    tot = 0
                    for i in orderD:
                        tot += i.unit_price * i.quantity * 100
                    res = UserT[orderQ.id_client].balance + tot
                    UserT.update({UserT.balance : res}).where(UserT.id == orderQ.id_client).execute()
                Order.update({Order.id_status : Status.CANCELED.value}).where(Order.id == orderQ.id).execute()
                return "", 200
            api.abort(404, f"Order already finished")
        except Order.DoesNotExist:
            api.abort(404, f"Error")

@api.route("/finish")
class OrderAPIfinish(Resource):
    @api.doc("finish_order")
    @api.expect(orderValidate,validate=True)
    @api.marshal_with(orderModelRead, code=201)
    def put(self):
        """Finish an order"""
        try:
            payload = {x: api.payload[x] for x in api.payload if x in orderValidate}
            if Order[payload["id"]].id_status.id == Status.VALIDATED.value:
                Order.update({Order.id_manager:payload["id_manager"],Order.id_status:Status.FINISHED.value}).where(Order.id == payload["id"]).execute()
                return model_to_dict(Order[payload["id"]]),201
            api.abort(404, f"Order not ready")
        except Order.DoesNotExist:
            api.abort(404, f"Error")

@api.route("/items")
class OrderAPI(Resource):
    @api.doc("new_order_item")
    @api.expect(items, validate=True)
    @api.marshal_with(items, code=201)
    def put(self):
        """Add or update an item in a specified order"""
        payload = {x: api.payload[x] for x in api.payload if x in items}
        payload["unit_price"] = 1
        query = OrderDetail.select().where(OrderDetail.id_order==payload["id_order"] and OrderDetail.id_product==payload["id_product"]) 
        if not query.exists():
            order = OrderDetail(**payload)
            order.save(force_insert=True)
            return model_to_dict(order),201
        else:
            q = OrderDetail.update(**payload).where((OrderDetail.id_order==payload["id_order"] and OrderDetail.id_product==payload["id_product"]))
            q.execute()
            return payload, 201
    @api.doc("delete_order_item")
    @api.expect(itemsBase, validate=True)
    @api.response(204, "Item deleted")
    def delete(self):
        """Delete a item given its identifier in a order"""
        payload = {x: api.payload[x] for x in api.payload if x in itemsBase}
        try:
            OrderDetail.delete().where(OrderDetail.id_order==payload["id_order"] and OrderDetail.id_product==payload["id_product"]).execute()
        except OrderDetail.DoesNotExist:
            api.abort(404, f"Order item do not exist")
        return "", 204
        

@api.route("/<string:id>")
@api.param("id", "The order  identifier")
class OrderIDAPI(Resource):
    @api.doc("get_order")
    @is_manager(api)
    @api.marshal_with(orderModelRead, code=201)
    def get(self,id):
        try:
            order = Order[id]
            x = []
            for item in OrderDetail.select().where(OrderDetail.id_order==id):
                x.append(model_to_dict(item))
            
            to_ret = model_to_dict(order)
            to_ret["item_list"] = x
            if to_ret["id_manager"] is None:
                to_ret["id_manager"] = -1
            return to_ret
        except Order.DoesNotExist:
            api.abort(404, f"Order {id} does not exist")
    
    

def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([Order,OrderDetail,Stats])