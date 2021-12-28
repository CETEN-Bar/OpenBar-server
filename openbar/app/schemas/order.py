#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field
from pydantic.utils import GetterDict

from models.order import OrderStatus
import peewee as pw


class OrderGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == 'client':
            return self._obj.client.id
        elif key == 'barman':
            if self._obj.barman is None:
                return default
            return self._obj.barman.id
        res = getattr(self._obj, key, default)
        if isinstance(res, pw.ModelSelect):
            return list(res)
        return res


class Order(BaseModel):
    id: Optional[int] = Field(None, description='Order id')
    client: int = Field(..., description='Id of the client')
    barman: Optional[int] = Field(None, description='ID of the barman that changed the order')
    status: OrderStatus = Field(..., description='Order status')
    created_at: Optional[datetime.datetime] = Field(None, description="")
    validated_at: Optional[datetime.datetime] = Field(None, description="")
    ended_at: Optional[datetime.datetime] = Field(None, description="")

    class Config:
        orm_mode = True
        getter_dict = OrderGetter
        use_enum_values = True


class OrderProductGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == 'order':
            return self._obj.order.id
        # elif key == 'product':
        #    return self._obj.product.id
        res = getattr(self._obj, key, default)
        if isinstance(res, pw.ModelSelect):
            return list(res)
        return res


class OrderProduct(BaseModel):
    order: int = Field(..., description='Order id')
    product: int = Field(..., description='Product id that is in the order')
    unit_price: int = Field(..., description='Price of the product when added')
    quantity: int = Field(..., description='Quantity of the product in this order')

    class Config:
        orm_mode = True
        getter_dict = OrderProductGetter
