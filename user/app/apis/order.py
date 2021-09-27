#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for ordering
"""

from flask_restx import Namespace, Resource, fields
from peewee import *
from playhouse.shortcuts import model_to_dict
from datetime import date
import logging

from models.order import Order as OrderDAO, OrderDetail as OrderDetailDAO
from tools.auth import is_password_logged, is_token_logged, is_barman, is_fully_logged

log = logging.getLogger(__name__)

api = Namespace('order', description='order')

items = api.model('Item list', {
    'id_product': fields.Integer,
    'quantity': fields.Integer,
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
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("new_order", security='password')
    @api.expect(orderModel, validate=True)
    @api.marshal_with(orderModel, code=201)
    def post(self):
        payload = {x: api.payload[x] for x in api.payload if x in orderModel}
        payload['id'] = len(OrderDAO) + 1
        payload_order = {"id":payload['id'],"id_manager" : payload["id_manager"] , "id_client" : payload["id_client"]}
        order = OrderDAO(**payload_order)
        order.save(force_insert=True)
        for item in payload["item_list"]:
            item["id_order"] = payload['id']
            item["quantity"] = 1
            item["unit_price"] = 1
            x = OrderDetailDAO(**item)
            x.save(force_insert=True)
        return payload, 201

@api.route("/<string:id>")
@api.param("id", "The order  identifier")
class OrderIDAPI(Resource):
    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    @api.doc("get_order", security='password')
    @api.marshal_with(orderModelRead, code=201)
    def get(self,id):
        order = OrderDAO[id]
        x = []
        for item in OrderDetailDAO.select().where(OrderDetailDAO.id_order==id):
            x.append(model_to_dict(item))
        
        to_ret = model_to_dict(order)
        to_ret["item_list"] = x
        return to_ret
