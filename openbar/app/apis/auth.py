#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for authentification
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from models.user import User, search_user, verify_user_password, \
    update_last_login
from tools.auth import login_user
from tools.db import get_db

local_history = []

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/token", dependencies=[Depends(get_db)])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login an user using its identifier.
    You must follow one of these cases
    - card_id : partial login
    - card_id with password : normal login
    - username with password : normal login
    - token : token renewal

    The "username" field must either :
    - begin by "username:" followed by the username
    - begin by "card_id:" followed by the cardID
    - begin by "token:" followed by a token

    The token can be renewed here after its expiration.
    The time of validity can be set in config.py with TOKEN_VALIDITY_TIME.
    """
    incorrect = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    partial_login = len(form_data.password) <= 0
    user = None
    if not partial_login and form_data.username.startswith('username:'):
        try:
            username = form_data.username.removeprefix('username:')
            user = User.get(User.username == username)
        except User.DoesNotExist:
            raise incorrect
    elif form_data.username.startswith('card_id:'):
        card_id = form_data.username.removeprefix('card_id:')
        user = search_user(card_id)
        if user is None:
            raise incorrect
    elif form_data.username.startswith('token:'):
        token = form_data.username.removeprefix('token:')
        # TODO: implement token renewal
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="""Incorrect request.
            Username doesn't give any information. Have you added the correct prefix ?
            Please see API documentation for more information.""",
            headers={"WWW-Authenticate": "Bearer"},
        )
    local_history.append(user.id)

    if not partial_login and not verify_user_password(user, form_data.password):
        raise incorrect

    # User is now authenticated, we can proceed
    update_last_login(user)
    token = login_user(user, partial_login)
    return {"access_token": token, "token_type": "bearer"}


@router.get('/history', dependencies=[Depends(get_db)])
def get_history() -> List[int]:
    """
    Fetch the history
    """
    # TODO: Correctly save history
    return local_history
