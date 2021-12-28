#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API of Roles
"""
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import Response

from schemas.role import RoleIn, RoleOut, RoleUpdate
from models.role import Role as RoleDAO, test_parent_validity
from tools.db import get_db

router = APIRouter(
    prefix="/role",
    tags=["role"],
)


@router.get('/', response_model=List[RoleOut], dependencies=[Depends(get_db)])
def role_user() -> List[RoleOut]:
    """
    List all roles
    """
    return list(RoleDAO.select())


@router.post('/', response_model=RoleOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_db)])
def create_role(body: RoleIn) -> RoleOut:
    """
    Create a new role
    """
    payload = body.dict()
    if payload['parent'] is not None:
        try:
            RoleDAO[body.parent]
        except RoleDAO.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The parent role doesn't exist")
    role = RoleDAO(**payload)
    role.save()
    return role


@router.delete('/', dependencies=[Depends(get_db)], status_code=status.HTTP_204_NO_CONTENT)
def delete_role() -> Response:
    """
    Delete all role
    """
    RoleDAO.delete().execute()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/{role_id}', response_model=RoleOut, dependencies=[Depends(get_db)])
def get_role(role_id: int) -> RoleOut:
    """
    Fetch a given role
    """
    try:
        role = RoleDAO[role_id]
        return role
    except RoleDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This role doesn't exist")


@router.put('/{role_id}', response_model=RoleOut, dependencies=[Depends(get_db)])
def update_role(role_id: int, body: RoleUpdate) -> RoleOut:
    """
    Update a given role
    """
    payload = body.dict(exclude_unset=True)
    try:
        if len(payload) == 0:
            return RoleDAO[role_id]
        role = RoleDAO[role_id]
        if 'parent' in payload and payload['parent'] is not None:
            try:
                test_parent_validity(role, RoleDAO[payload['parent']])
            except RoleDAO.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The parent doesn't exist")
        RoleDAO.update(**payload).where(RoleDAO.id == role_id).execute()
        return RoleDAO[role_id]
    except RoleDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This role doesn't exist")


@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_db)])
def delete_role(role_id: int) -> Response:
    """
    Delete a role given its identifier
    """
    try:
        RoleDAO[role_id].delete_instance()
    except RoleDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This role doesn't exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
