#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of methods to test a REST API
"""

import random
import requests


def get_all_one_equivalent(url):
    """Test that if getting the object separetly is the same
    as getting them all at the same time.
    """
    res = requests.get(url)
    assert res.status_code == 200
    for obj in res.json():
        res = requests.get(url + str(obj['id']))
        assert res.status_code == 200
        assert res.json() == obj


def unique_id(url, isequal):
    """Verivy that objects have unique ids"""
    res = requests.get(url)
    assert res.status_code == 200
    for obj in res.json():
        for obj2 in res.json():
            if obj['id'] == obj2['id']:
                isequal(obj, obj2)


def add_obj_and_verify(url, isequal, obj):
    """Add an object and verify that
    it was added and nothing else was touched
    """
    res = requests.get(url)
    assert res.status_code == 200
    obj_list_old = res.json()

    res = requests.post(url,
                        json=obj)
    assert res.status_code == 201
    obj_resulting = res.json()
    should_result = obj_resulting.copy()
    should_result.update(obj)
    isequal(obj_resulting, should_result)
    obj_id = obj_resulting['id']

    # Get all
    res = requests.get(url)
    assert res.status_code == 200
    assert len(obj_list_old) + 1 == len(res.json())
    for obj in res.json():
        if obj not in obj_list_old:
            assert obj['id'] == obj_id

    get_all_one_equivalent(url)
    unique_id(url, isequal)

    return obj_resulting


def delete_obj_and_verify(url, obj_id):
    """Delete an object and verify that is was deleted
    and nothing else was touched.
    """
    res = requests.get(url)
    assert res.status_code == 200
    obj_list_old = res.json()

    assert requests.delete(url + str(obj_id)) \
        .status_code == 204

    res = requests.get(url)
    assert res.status_code == 200
    obj_list = res.json()

    # Get all
    res = requests.get(url)
    assert res.status_code == 200
    assert len(obj_list_old) - 1 == len(obj_list)
    for obj in obj_list:
        if obj not in obj_list_old:
            assert obj['id'] == obj_id

    get_all_one_equivalent(url)


def update_obj_and_verify(url, obj_id, obj_update):
    """Update an object normaly and verify that is was updated
    and nothing else was touched.
    """
    res = requests.get(url)
    assert res.status_code == 200
    obj_list_old = res.json()

    res = requests.get(url + str(obj_id))
    assert res.status_code == 200
    actual_obj = res.json()

    # update
    res = requests.put(url + str(obj_id),
                       json=obj_update)
    assert res.status_code == 200
    actual_obj.update(obj_update)
    assert res.json() == actual_obj

    # Get all
    res = requests.get(url)
    assert res.status_code == 200
    assert len(obj_list_old) == len(res.json())
    for obj in res.json():
        if obj["id"] == obj_id:
            assert obj == actual_obj

    get_all_one_equivalent(url)

    return actual_obj


def tool_test_empty(url):
    """Test that everything is empty at the begining of the tests.
    Also delete everything.
    """
    assert requests.delete(url).status_code == 204
    res = requests.get(url)
    assert res.status_code == 200
    assert res.json() == []


def tool_test_add(url, isequal, minimal, full, random_obj):
    """Test adding objetcs
    minimal is an object with only the required attributes
    full is an object with all attributes
    random_obj is a function returning a random correct object
    """
    tool_test_empty(url)
    add_obj_and_verify(url, isequal, minimal)
    add_obj_and_verify(url, isequal, full)
    for _ in range(10):
        add_obj_and_verify(url, isequal, random_obj())


def tool_test_empty_all(url, isequal, random_obj):
    """Test the delete all functionality
    random_obj is a function returning a random correct object
    """
    for _ in range(random.randint(10, 20)):
        add_obj_and_verify(url, isequal, random_obj())
    tool_test_empty(url)


def tool_test_delete(url, isequal, random_obj):
    """Test deleting
    random_obj is a function returning a random correct object
    """
    tool_test_empty(url)
    for _ in range(10):
        add_obj_and_verify(url, isequal, random_obj())
    for _ in range(5):
        task = random_obj()
        task_id = add_obj_and_verify(url, isequal, task)['id']
        for _ in range(random.randint(0, 3)):
            add_obj_and_verify(url, isequal, random_obj())
        delete_obj_and_verify(url, task_id)
        for _ in range(random.randint(0, 3)):
            add_obj_and_verify(url, isequal, random_obj())


def tool_test_update(url, isequal, random_obj, random_obj_parts):
    """Test updating
    random_obj is a function returning a random correct object
    random_obj_parts is a function returning a random partial object
    """
    tool_test_empty(url)
    for _ in range(15):
        add_obj_and_verify(url, isequal, random_obj())
        res = requests.get(url)
        assert res.status_code == 200
        for task in res.json():
            update_obj_and_verify(url, task['id'], random_obj_parts())
