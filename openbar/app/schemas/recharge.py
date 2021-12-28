from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field
from pydantic.utils import GetterDict
import peewee as pw


class RechargeGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == 'client':
            return self._obj.client.id
        elif key == 'barman':
            return self._obj.barman.id
        res = getattr(self._obj, key, default)
        if isinstance(res, pw.ModelSelect):
            return list(res)
        return res


class RechargeIn(BaseModel):
    client: int = Field(..., description='Id of the client')
    value: int = Field(..., description='Recharge value * 100')

    class Config:
        orm_mode = True
        getter_dict = RechargeGetter


class RechargeOut(RechargeIn):
    id: int = Field(..., description='Recharge transaction id')
    barman: int = Field(..., description='Id of the barman who did the recharge')
    created_at: datetime = Field(..., description='Date of the recharge')

