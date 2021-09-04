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
from apis.role import Role
from flask_login import login_required, current_user
from tools.LoginManager import login_manager

log = logging.getLogger(__name__)

api = Namespace('recharge', description='Recharge')

class Recharge(db_wrapper.Model):
    id = IntegerField()
    id_manager= ForeignKeyField(UserT,backref="re")
    id_user_client = ForeignKeyField(UserT,backref="re")
    date = DateTimeField()
    value = IntegerField()

    class Meta:
        primary_key = CompositeKey('id','id_manager','id_user_client')


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
    @api.doc("new_recharge")
    @login_required
    @api.expect(rechargeModel, validate=True)
    @api.marshal_with(rechargeModel, code=201)
    def post(self):
        payload = {x: api.payload[x] for x in api.payload if x in rechargeModel}
        payload['id'] = len(Recharge)+1
        payload["date"] = str(date.today())
        if current_user.role.id == 1  and UserT[payload['id_manager']] == current_user:
            recharge = Recharge(**payload)
            recharge.save(force_insert=True)
            up = UserT.update(balance = UserT.balance+ payload['value']).where(UserT.id == payload['id_user_client'])
            up.execute()           
            payload["date"] = date.today()
            return model_to_dict(recharge), 201
        api.abort(404, f"Wrong creditencial")
        
    @login_required
    @api.marshal_list_with(rechargeModel)
    def get(self):
        re = Recharge.select()
        return [model_to_dict(s) for s in re]

def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([Recharge])
