#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example API for managing a task list
Inspired by
https://github.com/python-restx/flask-restx/blob/master/examples/todomvc.py
The licence of this file is availible at the end of this file.
"""

import os
import json

from flask_restx import Namespace, Resource, fields
from filelock import FileLock

from tools.auth import check_authorization

api = Namespace('basic', description='Example API')

FLNAME = "/tmp/basic.json"


def _get():
    "Return the content of FLNAME. Be carefull to have the file locked"
    if not os.path.isfile(FLNAME):
        _write([], 0)
        return [], 0
    with open(FLNAME, "r", encoding="utf-8") as file:
        return json.load(file)


def _write(tasks, counter):
    "Write to FLNAME. Be carefull to have the file locked"
    with open(FLNAME, "w", encoding="utf-8") as file:
        json.dump((tasks, counter), file)


class Tasks():
    """Object Database of a task"""
    def __init__(self):
        """Initialize an empty task list"""
        self.lock = FileLock(FLNAME + ".lock")

    def get_all(self):
        "Return all task"
        with self.lock:
            tasks, _ = _get()
            return tasks

    def get(self, id):
        """Return the task given its id"""
        with self.lock:
            tasks, _ = _get()
            for task in tasks:
                if task["id"] == id:
                    return task
        return api.abort(404, f"Task {id} doesn't exist")

    def create(self, data):
        """Create a task"""
        with self.lock:
            tasks, counter = _get()
            data["id"] = counter
            tasks.append(data)
            _write(tasks, counter + 1)
            return data

    def update(self, id, data):
        """Update a task"""
        with self.lock:
            tasks, counter = _get()
            for i in range(len(tasks)):
                if tasks[i]["id"] == id:
                    tasks[i].update(data)
                    _write(tasks, counter)
                    return tasks[i]
        return api.abort(404, f"Task {id} doesn't exist")

    def delete(self, id):
        """Delete the task given its id"""
        with self.lock:
            tasks, counter = _get()
            task = self.get(id)
            tasks.remove(task)
            _write(tasks, counter)

    def delete_all(self):
        """Delete the task given its id"""
        with self.lock:
            _write([], 0)


taskDAO = Tasks()

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
        return taskDAO.get_all()

    @api.doc("delete_tasks")
    @api.response(204, "tasks deleted")
    def delete(self):
        """Delete all tasks"""
        taskDAO.delete_all()
        return "", 204

    @api.doc("create_task")
    @api.expect(taskModel, validate=True)
    @api.marshal_with(taskModel)
    def post(self):
        """Create a new task"""
        return taskDAO.create(api.payload), 201


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
