#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Set of function to check authorization before accessing the API.
"""

from typing import Optional, List

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBasicCredentials, HTTPBasic
from starlette import status

from models.permission import LoginType
from models.user import User, verify_user_password, list_permissions
from tools.crypto import generate_user_token, decode_user_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)


def login_user(user, partial_login):
    """Return a token for a user."""
    lt = LoginType.NORMAL_LOGIN
    if partial_login:
        lt = LoginType.PARTIAL_LOGIN
    return generate_user_token(user.id, list_permissions(user, lt))


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme),
                           credentials: Optional[HTTPBasicCredentials] = Depends(basic_scheme))\
        -> tuple[User, List[str]]:
    if credentials is not None:
        # Checking Username/Password auth
        incorrect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        try:
            user = User.get(User.username == credentials.username)
        except User.DoesNotExist:
            raise incorrect
        if not verify_user_password(user, credentials.password):
            raise incorrect
        permissions = list_permissions(user, LoginType.PASSWORD)
        return user, permissions
    elif token is not None:
        # Checking token auth
        decoded = decode_user_token(token)
        if 'sub' not in decoded:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bad token no user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(decoded['sub'])
        try:
            user = User.get(User.id == user_id)
        except User.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if (not isinstance(decoded['aud'], list)
                or any(not isinstance(x, str) for x in decoded['aud'])):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        permissions = decoded['aud']
        return user, permissions
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
