#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for ordering
"""

from datetime import date
import logging
from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict

from models.order import Order as OrderDAO, OrderDetail as OrderDetailDAO
from tools.auth import is_password_logged, is_token_logged, is_barman, is_fully_logged

log = logging.getLogger(__name__)

api = Namespace('order', description='order')


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
    @is_token_logged(api)
    @api.doc("new_order")
    @api.expect(orderBaseModel, validate=True)
    @api.marshal_with(orderBaseModel, code=201)
    def post(self):
        """Create a new order in progress"""
        payload = {x: api.payload[x] for x in api.payload if x in orderBaseModel}
        payload['id_status'] = StatusEnum.INBASKET.value
        if 'id' in payload:
            payload.pop('id')
        order = OrderDAO(**payload)
        order.save(force_insert=True)
        return model_to_dict(order), 201

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("validate_basket")
    @api.expect(orderID,validate=True)
    @api.marshal_with(orderBaseModel, code=201)
    def put(self):
        """Validation of the basket"""
        payload = {x: api.payload[x] for x in api.payload if x in orderID}
        orderD = OrderDetailDAO.select().where(OrderDetailDAO.id_order==payload['id'])
        orderQ = OrderDAO[payload['id']]
        if orderQ.id_status.id == StatusEnum.INBASKET.value:
            tot = 0
            for i in orderD:
                tot += i.unit_price * i.quantity * 100
            if UserT[orderQ.id_client].balance >= tot:
                Order.update({Order.id_status : StatusEnum.VALIDATED.value}).where(Order.id == payload['id']).execute()
                res = UserT[orderQ.id_client].balance - tot
                UserT.update({UserT.balance : res}).where(UserT.id == orderQ.id_client).execute()
                return model_to_dict(Order[payload['id']]), 201
            api.abort(404, f"Not enought money")
        api.abort(404, f"Basket already validated")



@api.route("/cancel")
class OrderAPICancem(Resource):
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("cancel_order")
    @api.expect(orderID,validate=True)
    def put(self):
        """Cancel order and give money back if necessary"""
        try:
            payload = {x: api.payload[x] for x in api.payload if x in orderID}
            orderD = OrderDetailDAO.select().where(OrderDetailDAO.id_order==payload['id'])
            orderQ = OrderDAO[payload['id']]
            if orderQ.id_status.id != StatusEnum.FINISHED.value:
                if orderQ.id_status.id == StatusEnum.VALIDATED.value:
                    tot = 0
                    for i in orderD:
                        tot += i.unit_price * i.quantity * 100
                    res = UserT[orderQ.id_client].balance + tot
                    UserT.update({UserT.balance : res}).where(UserT.id == orderQ.id_client).execute()
                OrderDAO.update({OrderDAO.id_status : StatusEnum.CANCELED.value}).where(OrderDAO.id == orderQ.id).execute()
                return "", 200
            api.abort(404, f"Order already finished")
        except OrderDAO.DoesNotExist:
            api.abort(404, f"Error")

@api.route("/finish")
class OrderAPIfinish(Resource):
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("finish_order")
    @api.expect(orderValidate,validate=True)
    @api.marshal_with(orderModelRead, code=201)
    def put(self):
        """Finish an order"""
        try:
            payload = {x: api.payload[x] for x in api.payload if x in orderValidate}
            if OrderDAO[payload["id"]].id_status.id == StatusEnum.VALIDATED.value:
                OrderDAO.update({OrderDAO.id_manager:payload["id_manager"], OrderDAO.id_status:StatusEnum.FINISHED.value}).where(OrderDAO.id == payload["id"]).execute()
                return model_to_dict(OrderDAO[payload["id"]]),201
            api.abort(404, f"Order not ready")
        except OrderDAO.DoesNotExist:
            api.abort(404, f"Error")

@api.route("/items")
class OrderAPI(Resource):
    @is_token_logged(api)
    @api.doc("new_order_item")
    @api.expect(items, validate=True)
    @api.marshal_with(items, code=201)
    def put(self):
        """Add or update an item in a specified order"""
        payload = {x: api.payload[x] for x in api.payload if x in items}
        payload["unit_price"] = 1
        query = OrderDetailDAO.select().where(OrderDetailDAO.id_order==payload["id_order"] and OrderDetailDAO.id_product==payload["id_product"]) 
        if not query.exists():
            order = OrderDetailDAO(**payload)
            order.save(force_insert=True)
            return model_to_dict(order),201
        else:
            q = OrderDetailDAO.update(**payload).where((OrderDetailDAO.id_order==payload["id_order"] and OrderDetailDAO.id_product==payload["id_product"]))
            q.execute()
            return payload, 201

    @is_token_logged(api)
    @api.doc("delete_order_item")
    @api.expect(itemsBase, validate=True)
    @api.response(204, "Item deleted")
    def delete(self):
        """Delete a item given its identifier in a order"""
        payload = {x: api.payload[x] for x in api.payload if x in itemsBase}
        try:
            OrderDetailDAO.delete().where(OrderDetailDAO.id_order==payload["id_order"] and OrderDetailDAO.id_product==payload["id_product"]).execute()
        except OrderDetailDAO.DoesNotExist:
            api.abort(404, f"Order item do not exist")
        return "", 204
        

@api.route("/<string:id>")
@api.param("id", "The order  identifier")
class OrderIDAPI(Resource):
    @is_token_logged(api)
    @is_barman(api)
    @api.doc("get_order")
    @api.marshal_with(orderModelRead, code=201)
    def get(self,id):
        try:
            order = OrderDAO[id]
            x = []
            for item in OrderDetailDAO.select().where(OrderDetailDAO.id_order==id):
                x.append(model_to_dict(item))
            
            to_ret = model_to_dict(order)
            to_ret["item_list"] = x
            if to_ret["id_manager"] is None:
                to_ret["id_manager"] = -1
            return to_ret
        except OrderDAO.DoesNotExist:
            api.abort(404, f"Order {id} does not exist")
