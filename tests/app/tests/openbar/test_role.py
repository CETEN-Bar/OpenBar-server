#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the basic example API
"""

import random
import unittest
import requests

from tests.tools.random import random_string, random_boolean
from tests.tools.rest import (get_all_one_equivalent, add_obj_and_verify,
                              tool_test_empty, tool_test_add, tool_test_empty_all,
                              tool_test_delete, tool_test_update)

from tests.openbar import API_ROOT

ROOT = API_ROOT + "role/"

EXAMPLE_FULL = {
    "name": "Groupe sans respect",
}

EXAMPLE_MINIMAL = {
    "name": "Chouchou de michele"
}


def is_role_equal(role1, role2):
    """Test if two role are equals"""
    assert role1 == role2


def is_role_list_equal(role_list):
    """Check if role_list is the reflection of the API"""
    res = requests.get(ROOT)
    assert res.status_code == 200
    case = unittest.TestCase()
    case.assertCountEqual(role_list, res.json())


def random_role():
    """Return a random role"""
    role = {'name': random_string()}
    return role


def random_role_parts():
    """Return a random role without at all time required attribute"""
    role = {}
    if random_boolean():
        role['name'] = random_string()
    return role


def test_empty():
    """Test that everything is empty at the begining of the tests.
    Also delete everything.
    """
    tool_test_empty(ROOT)


def test_add():
    """Test adding roles"""
    tool_test_add(ROOT, is_role_equal,
                  EXAMPLE_MINIMAL, EXAMPLE_FULL, random_role)


def test_empty_all():
    """Test the delete all functionality"""
    tool_test_empty_all(ROOT, is_role_equal, random_role)


def test_delete():
    """Test deleting roles"""
    tool_test_delete(ROOT, is_role_equal, random_role)


def test_update():
    """Test updating a role"""
    tool_test_update(ROOT, is_role_equal, random_role, random_role_parts)


def test_not_exist():
    """Test getting, updating and deleting role that does not exists"""
    test_empty()
    role_list = []
    for i in range(10):
        if i in (0, 1, 2, 9):
            res = requests.get(ROOT)
            assert res.status_code == 200
            the_max = -1
            for role in res.json():
                the_max = max(the_max, role['id'])
            the_max += 1
            for _ in range(10):
                assert requests.delete(ROOT
                                       + str(random.randint(the_max,
                                                            the_max + 20))) \
                           .status_code == 404
            for _ in range(10):
                assert requests.get(ROOT
                                    + str(random.randint(the_max,
                                                         the_max + 20))) \
                           .status_code == 404
            for _ in range(10):
                assert requests.put(ROOT
                                    + str(random.randint(the_max,
                                                         the_max + 20)),
                                    json=random_role_parts()) \
                           .status_code == 404
            is_role_list_equal(role_list)
        role_list.append(add_obj_and_verify(ROOT,
                                            is_role_equal,
                                            random_role()))
    get_all_one_equivalent(ROOT)


def test_add_required_args():
    """Test adding roles without all required atributes"""
    test_empty()
    role_list = []
    for i in range(5):
        role_list.append(add_obj_and_verify(ROOT,
                                            is_role_equal,
                                            random_role()))
        if i in (0, 1, 5):
            assert requests.post(ROOT) \
                       .status_code in (400, 422)
            assert requests.post(ROOT,
                                 json={}) \
                       .status_code in (400, 422)
            assert requests.post(ROOT,
                                 json={"parent": 0}) \
                       .status_code in (400, 422)
            is_role_list_equal(role_list)
    get_all_one_equivalent(ROOT)


def test_readonly_attribute():
    """Test adding readonly attributes to input"""
    test_empty()
    role_list = []

    for _ in range(3):
        role_list.append(add_obj_and_verify(ROOT,
                                            is_role_equal,
                                            random_role()))
        role = EXAMPLE_MINIMAL.copy()
        role['id'] = role_list[random.randint(0, len(role_list) - 1)]['id']
        res = requests.post(ROOT,
                            json=role)
        assert res.status_code == 201
        assert res.json() != role['id']
        role_list.append(res.json())

        is_role_list_equal(role_list)

        role = EXAMPLE_MINIMAL.copy()
        role['id'] = random.randint(-200, -1)
        res = requests.post(ROOT,
                            json=role)
        assert res.status_code == 201
        assert res.json() != role['id']
        role_list.append(res.json())

        is_role_list_equal(role_list)

        ind = random.randint(0, len(role_list) - 1)
        role = random_role()
        role['id'] = role_list[random.randint(0, len(role_list) - 1)]['id']
        res = requests.put(ROOT + str(role_list[ind]['id']),
                           json=role)
        assert res.status_code == 200
        assert res.json()['id'] == role_list[ind]['id']
        role_list[ind] = res.json()

        is_role_list_equal(role_list)

        ind = random.randint(0, len(role_list) - 1)
        role = random_role()
        role['id'] = random.randint(100, 200)
        res = requests.put(ROOT + str(role_list[ind]['id']),
                           json=role)
        assert res.status_code == 200
        assert res.json()['id'] == role_list[ind]['id']
        role_list[ind] = res.json()

        is_role_list_equal(role_list)
    get_all_one_equivalent(ROOT)


def test_unwanted_attribute():
    """Test adding unwanted attributes to input"""
    test_empty()
    role_list = []
    for _ in range(3):
        role = random_role()
        attribute = random_string()
        while attribute in EXAMPLE_FULL:
            attribute = random_string()
        role[attribute] = random_string()
        res = requests.post(ROOT,
                            json=role)
        assert res.status_code == 201
        assert attribute not in res.json()
        role_list.append(res.json())

        is_role_list_equal(role_list)

        ind = random.randint(0, len(role_list) - 1)
        role = random_role()
        role[attribute] = random_string()
        res = requests.put(ROOT + str(role_list[ind]['id']),
                           json=role)
        assert res.status_code == 200
        assert attribute not in res.json()
        role_list[ind] = res.json()

        is_role_list_equal(role_list)
        role_list.append(add_obj_and_verify(ROOT,
                                            is_role_equal,
                                            random_role()))
    get_all_one_equivalent(ROOT)


def test_wrong_type():
    """Test change with wrong types"""
    test_empty()
    role_list = []
    ind = None

    def update_add_fail(role, allowed_status={400, 422}):
        """Check if the update and add of the role fail"""
        res = requests.post(ROOT, json=role)
        assert res.status_code in allowed_status
        if len(role_list) != 0:
            res = requests.put(ROOT + str(role_list[ind]['id']),
                               json=role)
            assert res.status_code in allowed_status

    for _ in range(10):
        if len(role_list) != 0:
            ind = random.randint(0, len(role_list) - 1)

        role = EXAMPLE_FULL.copy()
        role['parent'] = "abcd"
        update_add_fail(role)

        role_list.append(add_obj_and_verify(ROOT,
                                            is_role_equal,
                                            random_role()))
    get_all_one_equivalent(ROOT)


def test_heritage():
    """
    Test the heritage system of roles
    """
    test_empty()
    role0 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Admin'})
    role1 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Modo', 'parent': role0['id']})
    role2 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client', 'parent': role1['id']})
    role3 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client2', 'parent': role1['id']})
    role4 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Other', 'parent': role2['id']})

    assert requests.delete(ROOT + str(role1['id'])).status_code == 204

    assert requests.get(ROOT + str(role1['id'])).status_code == 404
    assert requests.get(ROOT + str(role2['id'])).status_code == 404
    assert requests.get(ROOT + str(role3['id'])).status_code == 404
    assert requests.get(ROOT + str(role4['id'])).status_code == 404


def test_heritage_update():
    """
    Test the heritage system of roles with deletion after update
    """
    test_empty()
    role0 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Admin'})
    role1 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Modo', 'parent': role0['id']})
    role2 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client', 'parent': role1['id']})
    role3 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client2', 'parent': role1['id']})
    role4 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Other', 'parent': role2['id']})

    assert requests.put(ROOT + str(role3['id']), json={'parent': role0['id']}).status_code == 200

    res = requests.get(ROOT + str(role3['id']))
    assert res.status_code == 200
    role3bis = res.json()
    assert role3bis['parent'] == role0['id']
    assert role3bis['name'] == 'Client2'
    assert role3bis['id'] == role3['id']

    assert requests.delete(ROOT + str(role1['id'])).status_code == 204

    assert requests.get(ROOT + str(role1['id'])).status_code == 404
    assert requests.get(ROOT + str(role2['id'])).status_code == 404
    assert requests.get(ROOT + str(role4['id'])).status_code == 404

    res = requests.get(ROOT + str(role3['id']))
    assert res.status_code == 200
    is_role_equal(res.json(), role3bis)


def test_heritage_weird():
    """
    Test the heritage system of roles with weird cases
    """
    test_empty()
    role0 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Admin'})
    role1 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Modo', 'parent': role0['id']})
    role2 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client', 'parent': role1['id']})
    role3 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Client2', 'parent': role1['id']})
    role4 = add_obj_and_verify(ROOT, is_role_equal, {"name": 'Other', 'parent': role2['id']})

    # Test impossible value
    assert requests.put(ROOT + str(role2['id']), json={'parent': -10}).status_code == 404
    assert requests.put(ROOT + str(role2['id']), json={'parent': 100000}).status_code == 404

    # Test change and deletion of a self parent role
    assert requests.put(ROOT + str(role4['id']), json={'parent': role4['id']}).status_code in (400, 417)
    assert requests.delete(ROOT + str(role4['id'])).status_code == 204

    # Test deletion of parent
    assert requests.put(ROOT + str(role3['id']), json={'parent': None}).status_code == 200
    assert requests.get(ROOT + str(role3['id'])).json()['parent'] is None
    assert requests.delete(ROOT + str(role3['id'])).status_code == 204

    # Test case if the parent is the child
    assert requests.put(ROOT + str(role1['id']), json={'parent': role2['id']}).status_code in (400, 417)
    assert requests.delete(ROOT + str(role2['id'])).status_code == 204
