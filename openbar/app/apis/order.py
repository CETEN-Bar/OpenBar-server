#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for ordering
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from models.order import Order as OrderDAO, OrderProduct as OrderProductDAO, OrderStatus, validate_order,\
    cancel_order_by, finish_the_order
from models.user import User as UserDAO
from schemas.order import Order, OrderProduct
from tools.auth import get_current_user
from tools.db import get_db

router = APIRouter(
    prefix="/order",
    tags=["order"],
)


@router.get('/', response_model=List[Order], dependencies=[Depends(get_db)])
def get_orders() -> List[Order]:
    """
    Get all orders and baskets
    """
    return list(OrderDAO.select())


@router.get('/complete', response_model=List[Order], dependencies=[Depends(get_db)])
def get_complete_orders() -> List[Order]:
    """
    Get all orders without incomplete baskets
    """
    return list(OrderDAO.select().where(OrderDAO.status != OrderStatus.IN_BASKET.value))


@router.get('/{order_id}', response_model=List[OrderProduct], dependencies=[Depends(get_db)])
def get_order_product(order_id: int) -> List[OrderProduct]:
    """
    Get all product from an order
    """
    try:
        order = OrderDAO.get(OrderDAO.id == order_id)
        return list(order.products)
    except OrderDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This order doesn't exist")


@router.get('/basket/', response_model=List[OrderProduct], dependencies=[Depends(get_db)])
def get_basket(login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> List[OrderProduct]:
    """
    Get the products that are in the basket of the logged user
    """
    user = login_info[0]
    try:
        order = OrderDAO.get((OrderDAO.client == user) & (OrderDAO.status == OrderStatus.IN_BASKET.value))
        return list(order.products)
    except OrderDAO.DoesNotExist:
        return []


@router.delete('/basket', dependencies=[Depends(get_db)], status_code=status.HTTP_204_NO_CONTENT)
def empty_basket(login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> Response:
    """
    Delete all items in the basket of the logged user
    """
    user = login_info[0]
    try:
        query = OrderDAO.delete0().where((OrderDAO.client == user) & (OrderDAO.status == OrderStatus.IN_BASKET.value))
        query.execute()
    except OrderDAO.DoesNotExist:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/basket/items/{product_id}', response_model=Optional[OrderProduct], dependencies=[Depends(get_db)])
def add_item(product_id: int,
             quantity: int = 1,
             login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> Optional[OrderProduct]:
    """
    Add or update an item in the basket of the logged user
    """
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The quantity must be positive.")
    user = login_info[0]
    try:
        order = OrderDAO.get((OrderDAO.client == user) & (OrderDAO.status == OrderStatus.IN_BASKET.value))
    except OrderDAO.DoesNotExist:
        order = OrderDAO(client=user)
        order.save()

    if quantity == 0:
        try:
            query = OrderProductDAO.delete().where((OrderProductDAO.order == order)
                                                   & (OrderProductDAO.product == product_id))
            query.execute()
        except OrderProductDAO.DoesNotExist:
            pass
        return None
    # TODO: product price
    op, _ = OrderProductDAO.get_or_create(order=order,
                                          product=product_id,
                                          quantity=quantity,
                                          unit_price=1)
    return op


@router.put('/basket/validate', response_model=Order, dependencies=[Depends(get_db)])
def validate_basket(login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> Order:
    """
    Validate the basket of the logged user.
    After that the order will not be able to be changed.
    However the order will be cancellable.
    """
    user = login_info[0]
    try:
        order = OrderDAO.get((OrderDAO.client == user) & (OrderDAO.status == OrderStatus.IN_BASKET.value))
        validate_order(order)
        return order
    except OrderDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user have an empty basket")


@router.put('/cancel/{order_id}', response_model=Order, dependencies=[Depends(get_db)])
def cancel_order(order_id: int, login_info: tuple[UserDAO, List[str]] = Depends(get_current_user))\
        -> Order:
    """
    Cancel order and give money back if necessary
    """
    barman = login_info[0]
    try:
        order = OrderDAO.get(OrderDAO.id == order_id)
        if order.status == OrderStatus.FINISHED.value:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="This order is already finished")
        if order.status == OrderStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="This order is already canceled")
        cancel_order_by(order, barman)
        return order
    except OrderDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This order doesn't exist")


@router.put('/finish/{order_id}', response_model=Order, dependencies=[Depends(get_db)])
def finish_order(order_id: int, login_info: tuple[UserDAO, List[str]] = Depends(get_current_user)) -> Order:
    """
    Finish an order
    After that the order will no be cancellable
    """
    barman = login_info[0]
    try:
        order = OrderDAO.get(OrderDAO.id == order_id)
        if order.status == OrderStatus.FINISHED.value:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="This order is already finished")
        if order.status == OrderStatus.CANCELLED.value:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail="This order is already canceled")
        finish_the_order(order, barman)
        return order
    except OrderDAO.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This order doesn't exist")
