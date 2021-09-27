#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for recharges
"""

from flask_restx import Namespace, Resource, fields
from playhouse.shortcuts import model_to_dict
from datetime import date
import logging

from models.recharge import Recharge
from models.user import User

from tools.auth import is_password_logged, is_token_logged, is_barman, is_fully_logged

log = logging.getLogger(__name__)

api = Namespace('recharge', description='Recharge')

rechargeModel = api.model('Recharge',{
    'id': fields.Integer(
        readonly=True,
        description='Recharge transaction id'),
    'id_manager': fields.Integer(
        required=True,
        description='Id of the admin who did the recharge',
        attribute= lambda x: x['id_manager'] if type(x['id_manager']) is int else x['id_manager']['id']),
    'id_user_client': fields.Integer(
        required=True,
        description='Id of the client',
        attribute= lambda x: x['id_user_client'] if type(x['id_user_client']) is int else x['id_user_client']['id']),
    'date': fields.Date(
        readonly=True,
        description='Date of the recharge'),
    'value': fields.Integer(
        required=True,
        description='Recharge value * 100'),
})


@api.route("/")
class RechargeAPI(Resource):
    """Show a list of every recharge and let you add more"""
    @is_password_logged(api)
    @is_barman(api)
    @api.doc("new_recharge", security='password')
    @api.expect(rechargeModel, validate=True)
    @api.marshal_with(rechargeModel, code=201)
    def post(self):
        payload = {x: api.payload[x] for x in api.payload if x in rechargeModel}
        payload['id'] = len(Recharge)+1
        payload["date"] = str(date.today())
        payload['value'] = payload['value'] * 100
        if current_user.role.id == 1  and UserT[payload['id_manager']] == current_user:
            recharge = Recharge(**payload)
            recharge.save(force_insert=True)
            up = User.update(balance = User.balance+ payload['value']).where(User.id == payload['id_user_client'])
            up.execute()           
            payload["date"] = date.today()
            return model_to_dict(recharge), 201
        api.abort(404, f"Wrong creditencial")
        
    @is_token_logged(api)
    @is_fully_logged(api)
    @is_barman(api)
    @api.doc("get_recharge", security='password')
    @api.marshal_list_with(rechargeModel)
    def get(self):
        re = Recharge.select()
        return [model_to_dict(s) for s in re]
