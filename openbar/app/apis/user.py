#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API of User management
"""

from datetime import datetime
from typing import List, Any

from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from starlette.responses import Response

from models.cardsalt import CardSalt
from models.user import User as UserDAO, search_user
from models.role import Role as RoleDAO
from schemas.user import UserOut, UserIn, CardID, UserUpdate
from tools.auth import get_current_user
from tools.crypto import generate_salt, hash_password, hash_card_id
from tools.db import get_db

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get('/', response_model=List[UserOut], dependencies=[Depends(get_db)])
def list_user() -> List[UserOut]:
    """
    List all user
    """
    return list(UserDAO.select())


def verifying_secrets(payload: dict[str, Any]):
    """
    Replace password with its hash and verify that the card_id is unique
    when updating or creating an user.
    :param payload: the dict of the input
    """
    if search_user(payload['card_id']):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this card id already exist.")
    if payload['password'] != "":
        payload['password'] = hash_password(payload['password'],
                                            generate_salt())


@router.post('/', response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_db)])
def create_user(body: UserIn) -> UserOut:
    """
    Create a new user
    """
    payload = body.dict()

    if UserDAO.get_or_none(username=payload['username']) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An user with the same username already exists")
    if UserDAO.get_or_none(email=payload['email']) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An user with the same e-mail address already exists")

    try:
        RoleDAO[body.role]
    except RoleDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This role doesn't exist")
    try:
        payload['salt'] = CardSalt[datetime.today().year]
    except CardSalt.DoesNotExist:
        payload['salt'] = CardSalt(year=datetime.today().year,
                                   salt=generate_salt())
        payload['salt'].save(force_insert=True)

    verifying_secrets(payload)

    payload['card_id'] = hash_card_id(payload['card_id'],
                                      payload['salt'].salt)
    user_obj = UserDAO(**payload)
    user_obj.save()
    return user_obj


@router.get('/{user_id}', response_model=UserOut, dependencies=[Depends(get_db)])
def get_user(user_id: int) -> UserOut:
    """
    Get a user given its identifier
    """
    try:
        user = UserDAO.get(UserDAO.id == user_id)
    except UserDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user doesn't exist")
    return user


@router.get('/me/', response_model=UserOut, dependencies=[Depends(get_db)])
def get_logged_user(login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> UserOut:
    """
    Get the user corresponding to the auth headers
    """
    return login_info[0]


@router.put('/{user_id}', response_model=UserOut, dependencies=[Depends(get_db)])
def put_user(user_id: int, body: UserUpdate) -> UserOut:
    """
    Update a user given its identifier
    """
    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="This user doesn't exist")
    payload = body.dict(exclude_unset=True)
    if UserDAO.get_or_none(username=payload['username']) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An user with the same username already exists")
    if UserDAO.get_or_none(email=payload['email']) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An user with the same e-mail address already exists")
    verifying_secrets(payload)
    if 'card_id' in payload:
        try:
            user = UserDAO.get(user_id)
            payload['card_id'] = hash_card_id(payload['card_id'],
                                              user.salt.salt)
        except UserDAO.DoesNotExist:
            raise not_found
    try:
        UserDAO.update(**payload).where(UserDAO.id == user_id).execute()
    except UserDAO.DoesNotExist:
        raise not_found
    return UserDAO[user_id]


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_db)])
def delete_user(user_id: int) -> Response:
    """
    Delete a user given its identifier
    """
    try:
        UserDAO[user_id].delete_instance()
    except UserDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user doesn't exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/anonymize/{user_id}', dependencies=[Depends(get_db)])
def anonymize_user(user_id: int):
    """
    Anonymize a user given its identifier
    """
    try:
        user = UserDAO[user_id]
    except UserDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user doesn't exist")
    user.first_name = ""
    user.name = ""
    user.mail = None
    user.phone = None
    user.username = None
    user.group_year = None
    user.stats_agree = False
    user.save()


@router.get('/card/', response_model=UserOut, dependencies=[Depends(get_db)])
def get_user_with_card(body: CardID) -> UserOut:
    """
    Fetch a given user
    """
    user = search_user(body.card_id)
    if user is not False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this card ID doesn't exist")
    return user
