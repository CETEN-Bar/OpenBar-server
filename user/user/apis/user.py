#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from dateutil import parser

from flask_restx import Namespace, Resource, fields
from sqlalchemy import select, delete, update,ForeignKey,exc
from sqlalchemy.orm import relationship

import bcrypt
import sys

from tools.auth import check_authorization
from tools.db import db, get_session


local_history= []

api = Namespace('user', description='User')
class RoleDAO(db.Model):
    """role object"""
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    lib = db.Column(db.String,nullable=False)
    child = relationship('UserDAO')

class UserDAO(db.Model):
    """user object"""
    __tablename__ = 'user_table'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    id_card = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    role = db.Column(db.Integer,ForeignKey('role.id'),nullable=False)
    username = db.Column(db.String)
    password = db.Column(db.String)

userModel = api.model('User', {
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='User identifier'),
    'id_card': fields.String(
        required=True,
        description='User card identifier'),
    'name': fields.String(
        required=True,
        description='User name'),
    'fname': fields.String(
        required=True,
        description='User first name'),
    'balance': fields.Integer(
        required=True,
        description='User balance, multiplied by 100'),
    'role': fields.Integer(
        required=True,
        example=1,
        description='User\'s role identifier'),
    'username': fields.String(
        required=False,
        description='Username'),
    'password': fields.String(
        required=False,
        description='Password'),
})


@check_authorization
@api.route("/")
class userList(Resource):
    """Shows a list of all user"""
    @api.doc("list_user")
    @api.marshal_list_with(userModel)
    def get(self):
        """List all user"""
        users = get_session().execute(select(UserDAO)).scalars().all()
        return users

    @api.doc("delete_user")
    @api.response(204, "user deleted")
    def delete(self):
        """Delete all user"""
        ses = get_session()
        ses.execute(delete(UserDAO))
        ses.commit()
        return "", 204

    @api.doc("create_user")
    @api.expect(userModel, validate=True)
    @api.marshal_with(userModel, code=201)
    def post(self):
        """Create a new user"""
        payload = api.payload
        payload['id_card'] = str(bcrypt.hashpw(str.encode(payload['id_card']),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))
        user = UserDAO(**payload)
        ses = get_session()
        ses.add(user)
        ses.commit()
        return user, 201


@check_authorization
@api.route("/<string:id_card>")
@api.response(404, "task not found")
@api.param("id_card", "The user card identifier")
class User(Resource):
    """Show a single user item and lets you delete them"""
    @api.doc("get_task")
    @api.marshal_with(userModel)
    def get(self, id_card):
        """Fetch a given user"""
        try:
            ses = get_session()
            user = ses.execute(select(UserDAO).where(UserDAO.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.')))).scalar_one()
            local_history.insert(0,user.name+" "+user.fname)
            return user
        except exc.SQLAlchemyError:
            local_history.insert(0,"*******")
            


    @api.doc("delete_task")
    @api.response(204, "task deleted")
    def delete(self, id_card):
        """Delete a user given its identifier"""
        ses = get_session()
        ses.execute(delete(UserDAO).where(UserDAO.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))))
        ses.commit()
        return "", 204

    @api.expect(userModel)
    @api.marshal_with(userModel)
    def put(self, id_card):
        """Update a user given its identifier"""
        payload = api.payload
        if 'id' in payload:
            payload.pop('id')
        ses = get_session()
        ses.execute(update(UserDAO).where(UserDAO.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.'))).values(payload))
        ses.commit()
        return ses.execute(select(UserDAO).where(UserDAO.id_card == str(bcrypt.hashpw(str.encode(id_card),b'$2b$12$VMATDKC7/YGRh.SO5K5c3.')))).scalar_one()

@check_authorization
@api.route("/history")
class History(Resource):
    """Show the history of the NFC card reader. This history will reset each time you restart the app"""
    @api.doc("get_history")
    def get(self):
        """Fetch the history"""
        return local_history

            


# Original Licence of https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py

# BSD 3-Clause License

# Original work Copyright (c) 2013 Twilio, Inc
# Modified work Copyright (c) 2014 Axel Haustant
# Modified work Copyright (c) 2020 python-restx Authors

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
