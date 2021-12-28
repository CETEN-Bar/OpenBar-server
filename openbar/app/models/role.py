#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of Role model
"""
from typing import List

import peewee as pw
from fastapi import HTTPException
from starlette import status

from models.permission import Permission
from tools.db import db


class Role(pw.Model):
    """Model of a user role"""
    id = pw.AutoField()
    name = pw.CharField()
    parent = pw.ForeignKeyField('self', null=True, backref='children',
                                on_delete='CASCADE')

    class Meta:
        database = db


class RolePermission(Permission):
    """"Model for role permission"""
    role_id = pw.ForeignKeyField(Role,
                                 backref="permissions",
                                 on_delete='CASCADE')

    class Meta:
        database = db


def getChildren(role: Role) -> List[Role]:
    """Return the recursively role children of a given role"""
    children = []
    wait_stack = [role]
    while len(wait_stack) != 0:
        actual_role = wait_stack.pop()
        if actual_role in children:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="The parent can't be one of it's children.")
        children.append(actual_role)
        wait_stack += list(actual_role.children)
    return children


def test_parent_validity(child: Role, parent: Role) -> None:
    """Check the validly of the chosen parent
    It will check if the child is the parent or if parent is one of it's children
    """
    if child == parent:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="The parent can't be the role itself")
    if parent in getChildren(child):
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="The parent cannot be one of the children of its child")
