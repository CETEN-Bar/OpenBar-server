
from typing import Optional, Any

from pydantic import BaseModel, Field
from pydantic.utils import GetterDict
import peewee as pw

from schemas import AllOptional


class RoleGetter(GetterDict):
    def get(self, key: Any, default: Any = None) -> Any:
        if key == 'parent':
            if self._obj.parent is None:
                return default
            return self._obj.parent.id
        res = getattr(self._obj, key, default)
        if isinstance(res, pw.ModelSelect):
            return list(res)
        return res


class RoleIn(BaseModel):
    name: str = Field(..., description='Role name', example="Admin")
    parent: Optional[int] = Field(None, description='Parent Role (the parent role have more power than the child).')

    class Config:
        orm_mode = True
        getter_dict = RoleGetter


class RoleOut(RoleIn):
    id: Optional[int] = Field(None, description='Role identifier')


class RoleUpdate(RoleIn, metaclass=AllOptional):
    pass
