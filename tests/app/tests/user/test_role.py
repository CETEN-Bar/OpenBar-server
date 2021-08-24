#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for the basic example API
"""
import requests
import json
import random
from dateutil import parser
import unittest

from tools.random import random_string, random_boolean
from tools.rest import get_all_one_equivalent, delete_obj_and_verify, add_obj_and_verify, update_obj_and_verify, tool_test_empty, tool_test_add, tool_test_empty_all, tool_test_delete, tool_test_update


API_ROOT = "http://nginx/api/v0/user/role/"

EXAMPLE_FULL = \
{
    "lib": "Groupe sans respect"
}

EXAMPLE_MINIMAL = \
{
    "lib": "Chouchou de michele"
}


def is_role_equal(role1, role2):
    """Test if two role are equals"""
    assert role1 ==  role2

def is_role_list_equal(list):
    """Check if the list is the reflection of the API"""
    res = requests.get(API_ROOT)
    assert res.status_code == 200
    case = unittest.TestCase()
    case.assertCountEqual(list, res.json())

def random_role():
    """Return a random role"""
    role = {}
    role['lib'] = random_string()
    return role

def random_role_parts():
    """Return a random role without at all time required attribute"""
    role = {}
    role['lib'] = random_string()
    return role

def test_empty():
    """Test that everything is empty at the begining of the tests.
    Also delete everything.
    """
    tool_test_empty(API_ROOT)

def test_add():
    """Test adding roles"""
    tool_test_add(API_ROOT, is_role_equal, EXAMPLE_MINIMAL, EXAMPLE_FULL, random_role)


def test_empty_all():
    """Test the delete all functionality"""
    tool_test_empty_all(API_ROOT, is_role_equal, random_role)

def test_delete():
    """Test deleting roles"""
    tool_test_delete(API_ROOT, is_role_equal, random_role)

def test_update():
    """Test updating a role"""
    tool_test_update(API_ROOT, is_role_equal, random_role, random_role_parts)

def test_not_exist():
    """Test getting, updating and deleting role that does not exists"""
    test_empty()
    rolelist = []
    for _ in range(10):
        res = requests.get(API_ROOT)
        assert res.status_code == 200
        themax = -1
        for role in res.json():
            themax = max(themax, role['id'])
        themax += 1
        for _ in range(10):
            assert requests.delete(API_ROOT + str(random.randint(themax, themax + 20))
                ).status_code == 404
        for _ in range(10):
            assert requests.get(API_ROOT + str(random.randint(themax, themax + 20))
                ).status_code == 404
        for _ in range(10):
            assert requests.put(API_ROOT + str(random.randint(themax, themax + 20)),
                json=random_role_parts()
                ).status_code == 404
        is_role_list_equal(rolelist)
        rolelist.append(add_obj_and_verify(API_ROOT, is_role_equal, random_role()))
    get_all_one_equivalent(API_ROOT)

def test_add_required_args():
    """Test adding roles without all required atributes"""
    test_empty()
    rolelist = []
    for _ in range(5):
        rolelist.append(add_obj_and_verify(API_ROOT, is_role_equal, random_role()))
        assert requests.post(API_ROOT
            ).status_code == 400
        assert requests.post(API_ROOT,
            json={}
            ).status_code == 400
        assert requests.post(API_ROOT,
            json={random_string(): random_string()}
            ).status_code == 400
        is_role_list_equal(rolelist)
    get_all_one_equivalent(API_ROOT)

def test_readonly_attribute():
    """Test adding readonly attributes to input"""
    test_empty()
    rolelist = []
    
    for _ in range(10):
        rolelist.append(add_obj_and_verify(API_ROOT, is_role_equal, random_role()))
        for id in (rolelist[random.randint(0, len(rolelist) - 1)]['id'], random.randint(-200, -1)):
            role = EXAMPLE_MINIMAL.copy()
            role['id'] = id
            res = requests.post(API_ROOT,
                json=role)
            assert res.status_code == 201
            assert res.json() != role['id']
            rolelist.append(res.json())
        
            is_role_list_equal(rolelist)

        for id in (rolelist[random.randint(0, len(rolelist) - 1)]['id'], random.randint(100, 200)):
            ind = random.randint(0, len(rolelist) - 1)
            role = random_role()
            role['id'] = id
            res = requests.put(API_ROOT + str(rolelist[ind]['id']),
                json=role)
            assert res.status_code == 200
            assert res.json()['id'] == rolelist[ind]['id']
            rolelist[ind] = res.json()

            is_role_list_equal(rolelist)

    get_all_one_equivalent(API_ROOT)


def test_unwanted_attribute():
    """Test adding unwanted attributes to input"""
    test_empty()
    rolelist = []
    for _ in range(10):
        role = random_role()
        attribute = random_string()
        while attribute in EXAMPLE_FULL:
            attribute = random_string()
        role[attribute] = random_string()
        res = requests.post(API_ROOT,
            json=role)
        assert res.status_code == 201
        assert attribute not in res.json()
        rolelist.append(res.json())

        is_role_list_equal(rolelist)

        ind = random.randint(0, len(rolelist) - 1)
        role = random_role()
        role[attribute] = random_string()
        res = requests.put(API_ROOT + str(rolelist[ind]['id']),
            json=role)
        assert res.status_code == 200
        assert attribute not in res.json()
        rolelist[ind] = res.json()

        is_role_list_equal(rolelist)
        rolelist.append(add_obj_and_verify(API_ROOT, is_role_equal, random_role()))
    get_all_one_equivalent(API_ROOT)

def test_wrong_type():
    """Test change with wrong types"""
    test_empty()
    rolelist = []
    ind = None
    def update_add_fail(role):
        """Check if the update and add of the role fail"""
        # "in (400, 500)" is Limitaion of flask restx
        # In theory it should always return 400
        assert requests.post(API_ROOT, json=role
            ).status_code in (400, 500)
        is_role_list_equal(rolelist)
        if len(rolelist) != 0:
            assert requests.put(API_ROOT + str(rolelist[ind]['id']), json=role
                ).status_code in (400, 500)
        is_role_list_equal(rolelist)
    for _ in range(10):
        if len(rolelist) != 0:
            ind = random.randint(0, len(rolelist) - 1)

        # role = EXAMPLE_FULL.copy()
        # role['deadline_date'] = random.randint(-50, 50)
        # update_add_fail(role)
        # role['deadline_date'] = random_boolean()
        # update_add_fail(role)
        # role['deadline_date'] = "abcd"
        # update_add_fail(role)

        # role = EXAMPLE_FULL.copy()
        # role['done'] = random.randint(-50, 50)
        # update_add_fail(role)
        # role['done'] = random_string()
        # update_add_fail(role)

        rolelist.append(add_obj_and_verify(API_ROOT, is_role_equal, random_role()))
    get_all_one_equivalent(API_ROOT)
