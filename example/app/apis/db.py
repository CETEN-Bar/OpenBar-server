#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example API for managing a task list using peewee.
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
The licence of this file is availible at the end of this file.
"""

from dateutil import parser

from flask_restx import Namespace, Resource, fields
import peewee as pw
from playhouse.shortcuts import model_to_dict

from tools.auth import check_authorization
from tools.db import db_wrapper

api = Namespace('db', description='Example API with db access')


class Task(db_wrapper.Model):
    """Object Database of a task"""
    __tablename__ = 'task'
    id = pw.AutoField()
    name = pw.CharField()
    description = pw.TextField(null=True)
    deadline_date = pw.DateTimeField(null=True)
    done = pw.BooleanField()


taskModel = api.model('task', {
    'id': fields.Integer(
        readonly=True,
        attribute='id',
        description='The task identifier'),
    'name': fields.String(
        required=True,
        description='The task name',
        example='Finish the example microservice'),
    'description': fields.String(
        required=False,
        description='The task description'),
    'deadline_date': fields.DateTime(
        required=False,
        description='The task deadline'),
    'done': fields.Boolean(
        required=True,
        description='If the task is done'),
})


@check_authorization
@api.route("/")
class TaskListAPI(Resource):
    """Shows a list of all tasks, and lets you POST to add new tasks"""
    @api.doc("list_tasks")
    @api.marshal_list_with(taskModel)
    def get(self):
        """List all tasks"""
        tasks = Task.select()
        return [model_to_dict(t) for t in tasks]

    @api.doc("delete_tasks")
    @api.response(204, "tasks deleted")
    def delete(self):
        """Delete all tasks"""
        Task.delete().execute()
        return "", 204

    @api.doc("create_task")
    @api.expect(taskModel, validate=True)
    @api.marshal_with(taskModel)
    def post(self):
        """Create a new task"""
        payload = {x: api.payload[x] for x in api.payload if x in taskModel}
        if 'id' in payload:
            payload.pop('id')
        if 'deadline_date' in payload:
            payload['deadline_date'] = parser.isoparse(
                                        payload['deadline_date'])
        task = Task(**payload)
        task.save()
        return model_to_dict(task), 201


@check_authorization
@api.route("/<int:id>")
@api.response(404, "task not found")
@api.param("id", "The task identifier")
class TaskAPI(Resource):
    """Show a single task item and lets you delete them"""
    @api.doc("get_task")
    @api.marshal_with(taskModel)
    def get(self, id):
        """Fetch a given task"""
        try:
            task = Task[id]
        except Task.DoesNotExist:
            api.abort(404, f"Task {id} doesn't exist")
        return model_to_dict(task)

    @api.doc("delete_task")
    @api.response(204, "task deleted")
    def delete(self, id):
        """Delete a task given its identifier"""
        try:
            Task[id].delete_instance()
        except Task.DoesNotExist:
            api.abort(404, f"Task {id} doesn't exist")
        return "", 204

    @api.expect(taskModel)
    @api.marshal_with(taskModel)
    def put(self, id):
        """Update a task given its identifier"""
        payload = {x: api.payload[x] for x in api.payload if x in taskModel}
        if 'id' in payload:
            payload.pop('id')
        try:
            if len(payload) == 0:
                return model_to_dict(Task[id])
            Task.update(**payload).where(Task.id == id).execute()
            return model_to_dict(Task[id])
        except Task.DoesNotExist:
            api.abort(404, f"Task {id} doesn't exist")


def create_tables():
    "Create tables for this file"
    db_wrapper.database.create_tables([Task])

# Original Licence of
# https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py

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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
