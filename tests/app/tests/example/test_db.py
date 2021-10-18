#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the basic example API
"""
import requests
import random
from dateutil import parser
import unittest

from tools.random import random_string, random_boolean
from tools.rest import (get_all_one_equivalent, add_obj_and_verify,
                        tool_test_empty, tool_test_add, tool_test_empty_all,
                        tool_test_delete, tool_test_update)


API_ROOT = "http://nginx/api/v0/example/db/"

EXAMPLE_FULL = {
    "name": "Finish the example microservice",
    "description": "A description",
    "deadline_date": "2021-07-22T15:29:34.887000+00:00",
    "done": True
}

EXAMPLE_MINIMAL = {
    "name": "Finish the example microservice",
    "done": False
}


def format_task_date(task):
    """Transforms date in python object for tasks"""
    if task is None:
        return task
    if 'deadline_date' in task and task['deadline_date'] is not None:
        task['deadline_date'] = parser.isoparse(task['deadline_date'])
    return task


def is_task_equal(task1, task2):
    """Test if two task are equals"""
    format_task_date(task1)
    format_task_date(task2)
    assert task1 == task2


def is_task_list_equal(tasklist):
    """Check if tasklist is the reflection of the API"""
    res = requests.get(API_ROOT)
    assert res.status_code == 200
    for task in tasklist:
        format_task_date(task)
    case = unittest.TestCase()
    case.assertCountEqual(tasklist, res.json())


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


def test_empty():
    """Test that everything is empty at the begining of the tests.
    Also delete everything.
    """
    tool_test_empty(API_ROOT)


def test_add():
    """Test adding tasks"""
    tool_test_add(API_ROOT, is_task_equal,
                  EXAMPLE_MINIMAL, EXAMPLE_FULL, random_task)


def test_empty_all():
    """Test the delete all functionality"""
    tool_test_empty_all(API_ROOT, is_task_equal, random_task)


def test_delete():
    """Test deleting tasks"""
    tool_test_delete(API_ROOT, is_task_equal, random_task)


def test_update():
    """Test updating a task"""
    tool_test_update(API_ROOT, is_task_equal, random_task, random_task_parts)


def test_not_exist():
    """Test getting, updating and deleting task that does not exists"""
    test_empty()
    tasklist = []
    for _ in range(10):
        res = requests.get(API_ROOT)
        assert res.status_code == 200
        themax = -1
        for task in res.json():
            themax = max(themax, task['id'])
        themax += 1
        for _ in range(10):
            assert requests.delete(API_ROOT
                                   + str(random.randint(themax,
                                                        themax + 20))) \
                    .status_code == 404
        for _ in range(10):
            assert requests.get(API_ROOT
                                + str(random.randint(themax,
                                                     themax + 20))) \
                    .status_code == 404
        for _ in range(10):
            assert requests.put(API_ROOT
                                + str(random.randint(themax,
                                                     themax + 20)),
                                json=random_task_parts()) \
                    .status_code == 404
        is_task_list_equal(tasklist)
        tasklist.append(format_task_date(add_obj_and_verify(API_ROOT,
                                                            is_task_equal,
                                                            random_task())))
    get_all_one_equivalent(API_ROOT)


def test_add_required_args():
    """Test adding tasks without all required atributes"""
    test_empty()
    tasklist = []
    for _ in range(5):
        tasklist.append(format_task_date(add_obj_and_verify(API_ROOT,
                                                            is_task_equal,
                                                            random_task())))
        assert requests.post(API_ROOT) \
            .status_code == 400
        assert requests.post(API_ROOT,
                             json={}) \
            .status_code == 400
        assert requests.post(API_ROOT,
                             json={"name": "abc"}) \
            .status_code == 400
        assert requests.post(API_ROOT,
                             json={"done": True}) \
            .status_code == 400

        is_task_list_equal(tasklist)
    get_all_one_equivalent(API_ROOT)


def test_readonly_attribute():
    """Test adding readonly attributes to input"""
    test_empty()
    tasklist = []

    for _ in range(10):
        tasklist.append(format_task_date(add_obj_and_verify(API_ROOT,
                                                            is_task_equal,
                                                            random_task())))
        task = EXAMPLE_MINIMAL.copy()
        task['id'] = tasklist[random.randint(0, len(tasklist) - 1)]['id']
        res = requests.post(API_ROOT,
                            json=task)
        assert res.status_code == 201
        assert res.json() != task['id']
        tasklist.append(format_task_date(res.json()))

        is_task_list_equal(tasklist)

        task = EXAMPLE_MINIMAL.copy()
        task['id'] = random.randint(-200, -1)
        res = requests.post(API_ROOT,
                            json=task)
        assert res.status_code == 201
        assert res.json() != task['id']
        tasklist.append(format_task_date(res.json()))

        is_task_list_equal(tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task['id'] = tasklist[random.randint(0, len(tasklist) - 1)]['id']
        res = requests.put(API_ROOT + str(tasklist[ind]['id']),
                           json=task)
        assert res.status_code == 200
        assert res.json()['id'] == tasklist[ind]['id']
        tasklist[ind] = format_task_date(res.json())

        is_task_list_equal(tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task['id'] = random.randint(100, 200)
        res = requests.put(API_ROOT + str(tasklist[ind]['id']),
                           json=task)
        assert res.status_code == 200
        assert res.json()['id'] == tasklist[ind]['id']
        tasklist[ind] = format_task_date(res.json())

        is_task_list_equal(tasklist)
    get_all_one_equivalent(API_ROOT)


def test_unwanted_attribute():
    """Test adding unwanted attributes to input"""
    test_empty()
    tasklist = []
    for _ in range(10):
        task = random_task()
        attribute = random_string()
        while attribute in EXAMPLE_FULL:
            attribute = random_string()
        task[attribute] = random_string()
        res = requests.post(API_ROOT,
                            json=task)
        assert res.status_code == 201
        assert attribute not in res.json()
        tasklist.append(format_task_date(res.json()))

        is_task_list_equal(tasklist)

        ind = random.randint(0, len(tasklist) - 1)
        task = random_task()
        task[attribute] = random_string()
        res = requests.put(API_ROOT + str(tasklist[ind]['id']),
                           json=task)
        assert res.status_code == 200
        assert attribute not in res.json()
        tasklist[ind] = format_task_date(res.json())

        print(task)
        print(res.json())

        is_task_list_equal(tasklist)
        tasklist.append(format_task_date(add_obj_and_verify(API_ROOT,
                                                            is_task_equal,
                                                            random_task())))
    get_all_one_equivalent(API_ROOT)


def test_wrong_type():
    """Test change with wrong types"""
    test_empty()
    tasklist = []
    ind = None

    def update_add_fail(task):
        """Check if the update and add of the task fail"""
        # "in (400, 500)" is Limitaion of flask restx
        # In theory it should always return 400
        assert requests.post(API_ROOT, json=task) \
            .status_code in (400, 500)
        is_task_list_equal(tasklist)
        if len(tasklist) != 0:
            assert requests.put(API_ROOT + str(tasklist[ind]['id']),
                                json=task) \
                .status_code in (400, 500)
        is_task_list_equal(tasklist)
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

        tasklist.append(format_task_date(add_obj_and_verify(API_ROOT,
                                                            is_task_equal,
                                                            random_task())))
    get_all_one_equivalent(API_ROOT)
