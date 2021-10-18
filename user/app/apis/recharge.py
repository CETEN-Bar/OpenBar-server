#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for recharges
"""
from datetime import date
import logging

from flask import g
from flask_restx import Namespace, Resource, fields
from playhouse.shortcuts import model_to_dict

from models.recharge import Recharge as RechargeDAO
from models.user import User as UserDAO

from tools.auth import is_password_logged, is_token_logged, is_barman, \
                        is_fully_logged

log = logging.getLogger(__name__)

api = Namespace('recharge', description='Recharge')

rechargeModel = api.model('Recharge', {
    'id': fields.Integer(
        readonly=True,
        description='Recharge transaction id'),
    'id_manager': fields.Integer(
        required=True,
        description='Id of the admin who did the recharge',
        attribute=lambda x: x['id_manager']
                    if isinstance(x['id_manager'], int)
                    else x['id_manager']['id']),
    'id_user_client': fields.Integer(
        required=True,
        description='Id of the client',
        attribute=lambda x: x['id_user_client']
                    if isinstance(x['id_user_client'], int)
                    else x['id_user_client']['id']),
    'date': fields.Date(
        readonly=True,
        description='Date of the recharge'),
    'value': fields.Integer(
        required=True,
        description='Recharge value * 100'),
})


@api.route("/")
class Recharge(Resource):
    """Show a list of every recharge and let you add more"""
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("new_recharge", security='password')
    @api.expect(rechargeModel, validate=True)
    @api.marshal_with(rechargeModel, code=201)
    def post(self):
        "Register an new recharge"
        payload = {x: api.payload[x] for x in api.payload
                   if x in rechargeModel}
        payload['id'] = len(RechargeDAO)+1
        payload["date"] = str(date.today())
        payload['value'] = payload['value'] * 100
        current_user = g
        if (current_user.role.id == 1
                and UserDAO[payload['id_manager']] == current_user):
            recharge = RechargeDAO(**payload)
            recharge.save(force_insert=True)
            req = UserDAO.update(balance=UserDAO.balance + payload['value']) \
                        .where(UserDAO.id == payload['id_user_client'])
            req.execute()
            payload["date"] = date.today()
            return model_to_dict(recharge), 201
        api.abort(404, "Wrong creditencial")

    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    @api.doc("get_recharge", security='password')
    @api.marshal_list_with(rechargeModel)
    def get(self):
        "Get all recharges"
        recharges = RechargeDAO.select()
        return [model_to_dict(s) for s in recharges]
