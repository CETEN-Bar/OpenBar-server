#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example API
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
"""

from flask_restx import Namespace, Resource, fields

from tools.auth import check_authorization

api = Namespace('basic', description='Example API')

class TasksDAO():
    """Object Database of a task"""
    def __init__(self):
        """Initialize an empty task list"""
        self.counter = 0
        self.tasks = []

    def get(self, id):
        """Return the task given its id"""
        for task in self.tasks:
            if task["id"] == id:
                return task
        return api.abort(404, f"Task {id} doesn't exist")

    def create(self, data):
        """Create a task"""
        task = data
        task["id"] = self.counter
        self.counter += 1
        self.tasks.append(task)
        return task

    def update(self, id, data):
        """Create a task"""
        task = self.get(id)
        task.update(data)
        return task

    def delete(self, id):
        """Delete the task given its id"""
        task = self.get(id)
        self.tasks.remove(task)

    def deleteAll(self):
        """Delete the task given its id"""
        self.tasks = []

taskDAO = TasksDAO()

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
class TaskList(Resource):
    """Shows a list of all tasks, and lets you POST to add new tasks"""
    @api.doc("list_tasks")
    @api.marshal_list_with(taskModel)
    def get(self):
        """List all tasks"""
        return taskDAO.tasks

    @api.doc("delete_tasks")
    @api.response(204, "tasks deleted")
    def delete(self):
        """Delete all tasks"""
        taskDAO.deleteAll()
        return "", 204

    @api.doc("create_task")
    @api.expect(taskModel, validate=True)
    @api.marshal_with(taskModel, code=201)
    def post(self):
        """Create a new task"""
        return taskDAO.create(api.payload), 201


@check_authorization
@api.route("/<int:id>")
@api.response(404, "task not found")
@api.param("id", "The task identifier")
class Task(Resource):
    """Show a single task item and lets you delete them"""
    @api.doc("get_task")
    @api.marshal_with(taskModel)
    def get(self, id):
        """Fetch a given task"""
        return taskDAO.get(id)

    @api.doc("delete_task")
    @api.response(204, "task deleted")
    def delete(self, id):
        """Delete a task given its identifier"""
        taskDAO.delete(id)
        return "", 204

    @api.expect(taskModel)
    @api.marshal_with(taskModel)
    def put(self, id):
        """Update a task given its identifier"""
        payload = api.payload
        if 'id' in payload:
            payload.pop('id')
        return taskDAO.update(id, payload)

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
