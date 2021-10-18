#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for ordering
"""

import logging
from flask_restx import Namespace, Resource, fields
from playhouse.shortcuts import model_to_dict

from models.order import Order as OrderDAO, OrderDetail as OrderDetailDAO, \
    StatusEnum
from models.user import User as UserDAO
from tools.auth import is_password_logged, is_token_logged, is_barman

log = logging.getLogger(__name__)

api = Namespace('order', description='order')


itemsBase = api.model('Item Base', {
    'id_order': fields.Integer(
        attribute=lambda x: x['id_order']
        if isinstance(x['id_order'], int) else x['id_order']['id']),
    'id_product': fields.Integer,
})

items = api.clone('Item list', itemsBase, {
    'quantity': fields.Integer,
})

orderlist_complete = api.clone('Order list', items, {
    'unit_price': fields.Integer,
})

orderID = api.model('Order ID', {
    'id': fields.Integer(
        description='Order id'),
})

orderValidate = api.clone('Order Validate', orderID, {
    'id_barman': fields.Integer(
        description='Manager id'),
})

orderBaseModel = api.model("Order", {
    'id': fields.Integer(
        readonly=True,
        description='Order id'),
    'id_client': fields.Integer(
        required=True,
        description='Id of the client',
        attribute=lambda x: x['id_client']
                    if isinstance(x['id_client'], int) else x['id_client']['id']),
    'id_status': fields.Integer(
        readonly=True,
        description='Order status',
        attribute=lambda x: x['id_status']
                    if isinstance(x['id_status'], int) else x['id_status']['id']),
})

orderModel = api.clone('Order Model', orderBaseModel, {
    'item_list': fields.List(fields.Nested(items)),
})

orderModelRead = api.clone('Order Read', orderBaseModel, {
    'id_barman': fields.Integer(
        required=True,
        description='Id of the barman who is responsible of the order',
        attribute=lambda x: x['id_barman']
                    if isinstance(x['id_barman'], int)
                    else x['id_barman']['id']),
    'item_list': fields.List(fields.Nested(orderlist_complete)),
})


orderFinishModel = api.model("Order Finish model", {
    'id': fields.Integer(
        description='Order id'),
    'id_barman': fields.Integer(
        required=True,
        description='Id of the barman who is responsible the order'),
})


@api.route("/")
class Order(Resource):
    """API to manage order"""
    @is_token_logged(api)
    @api.doc("new_order")
    @api.expect(orderBaseModel, validate=True)
    @api.marshal_with(orderBaseModel, code=201)
    def post(self):
        """Create a new order in progress"""
        payload = {x: api.payload[x] for x in api.payload
                   if x in orderBaseModel}
        payload['id_status'] = StatusEnum.INBASKET.value
        if 'id' in payload:
            payload.pop('id')
        order = OrderDAO(**payload)
        order.save(force_insert=True)
        return model_to_dict(order), 201

    @is_password_logged(api)
    @is_barman(api)
    @api.doc("validate_basket")
    @api.expect(orderID, validate=True)
    @api.marshal_with(orderBaseModel, code=201)

    def put(self):
        """Validation of the basket"""
        payload = {x: api.payload[x] for x in api.payload if x in orderID}
        order_details = OrderDetailDAO.select() \
                               .where(OrderDetailDAO.id_order == payload['id'])
        order = OrderDAO[payload['id']]
        if order.id_status.id == StatusEnum.INBASKET.value:
            tot = 0
            for i in order_details:
                tot += i.unit_price * i.quantity * 100
            if UserDAO[order.id_client].balance >= tot:
                OrderDAO.update({OrderDAO.id_status:
                                 StatusEnum.VALIDATED.value}) \
                        .where(OrderDAO.id == payload['id']) \
                        .execute()
                res = UserDAO[order.id_client].balance - tot
                UserDAO.update({UserDAO.balance: res}) \
                       .where(UserDAO.id == order.id_client) \
                       .execute()
                return model_to_dict(OrderDAO[payload['id']]), 201
            api.abort(404, "Not enought money")
        api.abort(404, "Basket already validated")


@api.route("/cancel")
class OrderCancel(Resource):
    """Api to cancel an order"""
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("cancel_order")
    @api.expect(orderID, validate=True)
    def put(self):
        """Cancel order and give money back if necessary"""
        try:
            payload = {x: api.payload[x] for x in api.payload if x in orderID}
            order_details = OrderDetailDAO.select() \
                .where(OrderDetailDAO.id_order == payload['id'])
            order = OrderDAO[payload['id']]
            if order.id_status.id != StatusEnum.FINISHED.value:
                if order.id_status.id == StatusEnum.VALIDATED.value:
                    tot = 0
                    for i in order_details:
                        tot += i.unit_price * i.quantity * 100
                    res = UserDAO[order.id_client].balance + tot
                    UserDAO.update({UserDAO.balance: res}) \
                           .where(UserDAO.id == order.id_client) \
                           .execute()
                OrderDAO.update({OrderDAO.id_status:
                                 StatusEnum.CANCELED.value}) \
                        .where(OrderDAO.id == order.id) \
                        .execute()
                return "", 200
        except OrderDAO.DoesNotExist:
            api.abort(404, "Error")
        api.abort(404, "Order already finished")


@api.route("/finish")
class OrderFinish(Resource):
    """API to mark an order as finished"""
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("finish_order")
    @api.expect(orderValidate, validate=True)
    @api.marshal_with(orderModelRead, code=201)
    def put(self):
        """Finish an order"""
        try:
            payload = {x: api.payload[x] for x in api.payload
                       if x in orderValidate}
            if OrderDAO[payload["id"]].id_status.id == \
                    StatusEnum.VALIDATED.value:
                OrderDAO.update({OrderDAO.id_barman:
                                 payload["id_barman"],
                                OrderDAO.id_status:
                                 StatusEnum.FINISHED.value}) \
                        .where(OrderDAO.id == payload["id"]) \
                        .execute()
                return model_to_dict(OrderDAO[payload["id"]]), 201
            api.abort(404, "Order not ready")
        except OrderDAO.DoesNotExist:
            api.abort(404, "Error")


@api.route("/items")
class Item(Resource):
    """API to manage item in an basket"""
    @is_token_logged(api)
    @api.doc("new_order_item")
    @api.expect(items, validate=True)
    @api.marshal_with(items, code=201)
    def put(self):
        """Add or update an item in a specified order"""
        payload = {x: api.payload[x] for x in api.payload if x in items}
        payload["unit_price"] = 1
        query = OrderDetailDAO.select() \
                              .where(OrderDetailDAO.id_order ==
                                     payload["id_order"]
                                     and OrderDetailDAO.id_product ==
                                     payload["id_product"])
        if not query.exists():
            order = OrderDetailDAO(**payload)
            order.save(force_insert=True)
            return model_to_dict(order), 201
        else:
            OrderDetailDAO.update(**payload) \
                          .where((OrderDetailDAO.id_order ==
                                 payload["id_order"]
                                 and OrderDetailDAO.id_product ==
                                 payload["id_product"])) \
                          .execute()
            return payload, 201

    @is_token_logged(api)
    @api.doc("delete_order_item")
    @api.expect(itemsBase, validate=True)
    @api.response(204, "Item deleted")
    def delete(self):
        """Delete a item given its identifier in a order"""
        payload = {x: api.payload[x] for x in api.payload if x in itemsBase}
        try:
            OrderDetailDAO.delete() \
                          .where(OrderDetailDAO.id_order ==
                                 payload["id_order"]
                                 and OrderDetailDAO.id_product ==
                                 payload["id_product"]) \
                          .execute()
        except OrderDetailDAO.DoesNotExist:
            api.abort(404, "Order item do not exist")
        return "", 204


@api.route("/<string:id>")
@api.param("id", "The order identifier")
class OrderID(Resource):
    """API to get details on an order"""
    @is_token_logged(api)
    @is_barman(api)
    @api.doc("get_order")
    @api.marshal_with(orderModelRead, code=201)
    def get(self, id):
        """Get details on an order"""
        try:
            order = OrderDAO[id]
            x = []
            for item in OrderDetailDAO.select() \
                                      .where(OrderDetailDAO.id_order == id):
                x.append(model_to_dict(item))

            to_ret = model_to_dict(order)
            to_ret["item_list"] = x
            if to_ret["id_barman"] is None:
                to_ret["id_barman"] = -1
            return to_ret
        except OrderDAO.DoesNotExist:
            api.abort(404, f"Order {id} does not exist")
