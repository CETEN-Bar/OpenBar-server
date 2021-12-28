#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for recharges
"""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from models.recharge import Recharge as RechargeDAO
from models.user import User as UserDAO
from schemas.recharge import RechargeIn, RechargeOut
from tools.auth import get_current_user
from tools.db import get_db

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/recharge",
    tags=["recharge", "user"],
)


@router.get('/', response_model=List[RechargeOut], dependencies=[Depends(get_db)])
def get_all_recharges() -> List[RechargeOut]:
    """
    Get all recharges
    """
    recharges = RechargeDAO.select()
    return list(recharges)


@router.get('/{recharge_id}', response_model=RechargeOut, dependencies=[Depends(get_db)])
def get_recharge(recharge_id: int) -> RechargeOut:
    """
    Get a recharge given its ID
    """
    try:
        recharge = RechargeDAO[recharge_id]
    except RechargeDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This recharge does not exist")
    return recharge


@router.post('/', response_model=RechargeOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_db)])
def new_recharge(body: RechargeIn,
                 login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> RechargeOut:
    """
    Create an new recharge
    """
    current_user = login_info[0]

    if body.value <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The value must be strictly positive.")

    try:
        user = UserDAO.get(UserDAO.id == body.client)
    except UserDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user doesn't exist.")

    recharge = RechargeDAO(barman=current_user, client=user, value=body.value, created_at=datetime.now())
    recharge.save()

    user.balance += body.value
    user.save()

    return recharge
