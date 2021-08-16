#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the db example API
"""

import random, string
from dateutil import parser
import unittest

from flask import url_for


EXAMPLE_FULL = \
{
    "name": "Finish the example microservice",
    "description": "A description",
    "deadline_date": "2021-07-22T15:29:34.887000+00:00",
    "done": True
}

EXAMPLE_MINIMAL = \
{
    "name": "Finish the example microservice",
    "done": False
}

def random_string():
    """Return a radom string"""
    return ''.join(random.choices(string.ascii_letters, k=random.randint(1, 50)))

def random_boolean():
    """Return a radom boolean"""
    return random.randint(0, 1) == 1

def random_task():
    """Return a random task"""
    task = {}
    task['name'] = random_string()
    task['done'] = random_boolean()
    if random_boolean():
        task['description'] = random_string()
    return task

def random_task_parts():
    """Return a random task without at all time required attribute"""
    task = {}
    if random_boolean():
        task['name'] = random_string()
    if random_boolean():
        task['done'] = random_boolean()
    if random_boolean():
        task['description'] = random_string()
    return task

def format_task_date(task):
    """Transforms date in python object for tasks"""
    if task == None:
        return task
    if 'deadline_date' in task and task['deadline_date'] != None:
        task['deadline_date'] = parser.isoparse(task['deadline_date'])
    return task


def is_task_equal(task1, task2):
    """Test if two task are equals"""
    format_task_date(task1)
    format_task_date(task2)
    assert task1 ==  task2


def get_all_one_equivalent(client):
    """Test that if getting the object separetly is the same
    as getting them all at the same time.
    """
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    for task in res.json:
        res = client.get(url_for('apis.db_task_api', id=task['id']))
        assert res.status_code == 200
        is_task_equal(res.json, task)

def unique_id(client):
    """Verivy that task have unique ids"""
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    for task in res.json:
        for task2 in res.json:
            if task['id'] == task2['id']:
                is_task_equal(task, task2)

def add_task_and_verify(client, task):
    """Add a task and verify that is was added and nothing else was touched"""
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    task_list_old = res.json

    res =  client.post(url_for('apis.db_task_list_api'),
            json=task)
    assert res.status_code == 201
    task_resulting = res.json
    task_should_result = task_resulting.copy()
    task_should_result.update(task)
    is_task_equal(task_resulting, task_should_result)
    task_id = task_resulting['id']

    # Get all
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    assert len(task_list_old) + 1 == len(res.json)
    for task in res.json:
        if task not in task_list_old:
            assert task['id'] == task_id

    get_all_one_equivalent(client)
    unique_id(client)

    return task_resulting

def delete_task_and_verify(client, task_id):
    """Delete a task and verify that is was deleted
    and nothing else was touched.
    """
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    task_list_old = res.json

    assert client.delete(url_for('apis.db_task_api',
            id=task_id),
        ).status_code == 204

    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    task_list = res.json

    # Get all
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    assert len(task_list_old) - 1 == len(task_list)
    for task in task_list:
        if task not in task_list_old:
            assert task['id'] == task_id

    get_all_one_equivalent(client)

def update_task_and_verify(client, task_id, task_update):
    """Update a task normaly and verify that is was updated
    and nothing else was touched.
    """
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    task_list_old = res.json

    res = client.get(url_for('apis.db_task_api', id=task_id))
    assert res.status_code == 200
    actual_task = res.json

    # update
    res = client.put(url_for('apis.db_task_api', id=task_id),
            json=task_update)
    assert res.status_code == 200
    actual_task.update(task_update)
    assert res.json == actual_task

    # Get all
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    assert len(task_list_old) == len(res.json)
    for task in res.json:
        if task not in task_list_old:
            assert task == actual_task

    get_all_one_equivalent(client)
    unique_id(client)

    return actual_task


def test_empty(client):
    """Test that everything is empty at the begining of the tests.
    Also delete everything.
    """
    assert client.delete(url_for('apis.db_task_list_api')).status_code == 204
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    assert res.json == []

def test_add(client):
    """Test adding tasks"""
    test_empty(client)
    add_task_and_verify(client, EXAMPLE_MINIMAL)
    add_task_and_verify(client, EXAMPLE_FULL)
    for _ in range(10):
        add_task_and_verify(client, random_task())

def test_empty_all(client):
    """Test the delete all functionality"""
    for _ in range(random.randint(10, 20)):
        add_task_and_verify(client, random_task())
    test_empty(client)

def test_delete(client):
    """Test deleting tasks"""
    test_empty(client)
    for _ in range(10):
        add_task_and_verify(client, random_task())
    for _ in range(5):
        task = random_task()
        task_id = add_task_and_verify(client, task)['id']
        for _ in range(random.randint(0, 3)):
            add_task_and_verify(client, random_task())
        delete_task_and_verify(client, task_id)
        for _ in range(random.randint(0, 3)):
            add_task_and_verify(client, random_task())

def test_update(client):
    """Test updating a task"""
    test_empty(client)
    for _ in range(15):
        add_task_and_verify(client, random_task())
        res = client.get(url_for('apis.db_task_list_api'))
        assert res.status_code == 200
        for task in res.json:
            update_task_and_verify(client, task['id'], random_task_parts())

def tasklist_ok(client, tasklist):
    """Check if tasklist is the reflection of the API"""
    res = client.get(url_for('apis.db_task_list_api'))
    assert res.status_code == 200
    for task in tasklist:
        format_task_date(tasklist)
    case = unittest.TestCase()
    case.assertCountEqual(tasklist, res.json)

def test_not_exist(client):
    """Test getting, updating and deleting task that does not exists"""
    test_empty(client)
    tasklist = []
    for _ in range(10):
        res = client.get(url_for('apis.db_task_list_api'))
        assert res.status_code == 200
        themax = -1
        for task in res.json:
            themax = max(themax, task['id'])
        themax += 1
        for _ in range(10):
            assert client.delete(url_for('apis.db_task_api',
                id=random.randint(themax, themax + 20))
                ).status_code == 404
        for _ in range(10):
            assert client.get(url_for('apis.db_task_api',
                id=random.randint(themax, themax + 20))
                ).status_code == 404
        for _ in range(10):
            assert client.put(url_for('apis.db_task_api',
                id=random.randint(themax, themax + 20)),
                json=random_task_parts()
                ).status_code == 404
        tasklist_ok(client, tasklist)
        tasklist.append(format_task_date(add_task_and_verify(client, random_task())))
    get_all_one_equivalent(client)

def test_add_required_args(client):
    """Test adding tasks without all required atributes"""
    test_empty(client)
    tasklist = []
    for _ in range(5):
        tasklist.append(format_task_date(add_task_and_verify(client, random_task())))
        assert client.post(url_for('apis.db_task_list_api')
            ).status_code == 400
        assert client.post(url_for('apis.db_task_list_api'),
            json={}
            ).status_code == 400
        assert client.post(url_for('apis.db_task_list_api'),
            json={"name": "abc"}
            ).status_code == 400
        assert client.post(url_for('apis.db_task_list_api'),
            json={"done": True}
            ).status_code == 400

        tasklist_ok(client, tasklist)
    get_all_one_equivalent(client)

def test_readonly_attribute(client):
    """Test adding readonly attributes to input"""
    test_empty(client)
    tasklist = []
    
    for _ in range(10):
        tasklist.append(format_task_date(add_task_and_verify(client, random_task())))
        task = EXAMPLE_MINIMAL.copy()
        task['id'] = tasklist[random.randint(0, len(tasklist) - 1)]['id']
        res = client.post(url_for('apis.db_task_list_api'),
            json=task)
        assert res.status_code == 201
        assert res.json != task['id']
        tasklist.append(format_task_date(res.json))

        tasklist_ok(client, tasklist)

        task = EXAMPLE_MINIMAL.copy()
        task['id'] = random.randint(-200, -1)
        res = client.post(url_for('apis.db_task_list_api'),
            json=task)
        assert res.status_code == 201
        assert res.json != task['id']
        tasklist.append(format_task_date(res.json))
        
        tasklist_ok(client, tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task['id'] = tasklist[random.randint(0, len(tasklist) - 1)]['id']
        res = client.put(url_for('apis.db_task_api', id=tasklist[ind]['id']),
            json=task)
        assert res.status_code == 200
        assert res.json['id'] == tasklist[ind]['id']
        tasklist[ind] = format_task_date(res.json)

        tasklist_ok(client, tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task['id'] = random.randint(100, 200)
        res = client.put(url_for('apis.db_task_api', id=tasklist[ind]['id']),
            json=task)
        assert res.status_code == 200
        assert res.json['id'] == tasklist[ind]['id']
        tasklist[ind] = format_task_date(res.json)

        tasklist_ok(client, tasklist)
    get_all_one_equivalent(client)


def test_unwanted_attribute(client):
    """Test adding unwanted attributes to input"""
    test_empty(client)
    tasklist = []
    for _ in range(10):
        task = random_task()
        attribute = random_string()
        while attribute in EXAMPLE_FULL:
            attribute = random_string()
        task[attribute] = random_string()
        res = client.post(url_for('apis.db_task_list_api'),
            json=task)
        assert res.status_code == 201
        assert attribute not in res.json
        tasklist.append(format_task_date(res.json))

        tasklist_ok(client, tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task[attribute] = random_string()
        res = client.put(url_for('apis.db_task_api', id=tasklist[ind]['id']),
            json=task)
        assert res.status_code == 200
        assert attribute not in res.json
        tasklist[ind] = format_task_date(res.json)

        tasklist_ok(client, tasklist)
        tasklist.append(format_task_date(add_task_and_verify(client, random_task())))
    get_all_one_equivalent(client)

def test_wrong_type(client):
    """Test change with wrong types"""
    test_empty(client)
    tasklist = []
    ind = None
    def update_add_fail(task):
        """Check if the update and add of the task fail"""
        # "in (400, 500)" is Limitaion of flask restx
        # In theory it should always return 400
        assert client.post(url_for('apis.db_task_list_api'), json=task
            ).status_code in (400, 500)
        tasklist_ok(client, tasklist)
        if len(tasklist) != 0:
            assert client.put(url_for('apis.db_task_api', id=tasklist[ind]['id']), json=task
                ).status_code in (400, 500)
        tasklist_ok(client, tasklist)
    for _ in range(10):
        if len(tasklist) != 0:
            ind = random.randint(0, len(tasklist) - 1)

        # task = EXAMPLE_FULL.copy()
        # task['deadline_date'] = random.randint(-50, 50)
        # update_add_fail(task)
        # task['deadline_date'] = random_boolean()
        # update_add_fail(task)
        # task['deadline_date'] = "abcd"
        # update_add_fail(task)

        # task = EXAMPLE_FULL.copy()
        # task['done'] = random.randint(-50, 50)
        # update_add_fail(task)
        # task['done'] = random_string()
        # update_add_fail(task)

        tasklist.append(add_task_and_verify(client, random_task()))
    get_all_one_equivalent(client)
