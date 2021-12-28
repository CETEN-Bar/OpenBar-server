
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field
from pydantic.utils import GetterDict
import peewee as pw

from schemas import AllOptional


class UserGetter(GetterDict):
    def get(self, key: Any, default: Any = None):
        if key == 'role':
            return self._obj.role.id
        res = getattr(self._obj, key, default)
        if isinstance(res, pw.ModelSelect):
            return list(res)
        return res


class UserBase(BaseModel):
    name: str = Field(..., description='User name', example='Sebastien')
    first_name: str = Field(..., description='User first name', example='Da Silva')
    role: int = Field(..., description="User's role identifier", example=1)
    group_year: Optional[int] = Field(
        None, description="User's group year", example=2023
    )
    username: Optional[str] = Field(
        None, description='Username', example='xXx_monSeigneur54_xXx'
    )
    phone: Optional[str] = Field(
        None, description='Phone number', example='01 02 03 04 05'
    )
    mail: Optional[str] = Field(
        None, description='Mail', example='xxmonseigneurxx@telecomnancy.eu'
    )
    stats_agree: bool = Field(
        ...,
        description='user agreement for us to use his data for stats',
        example=False,
    )

    class Config:
        orm_mode = True
        getter_dict = UserGetter


class UserOut(UserBase):
    id: Optional[int] = Field(None, description='User identifier')
    balance: Optional[int] = Field(
        None, description='User balance, multiplied by 100', example=100
    )
    last_login: Optional[datetime] = Field(None, description='Date of the last login')


class UserIn(UserBase):
    card_id: str = Field(..., description='User card identifier', example='04ABDC1234')
    password: Optional[str] = Field(None, description='Password', example='BouthierUWU')


class UserUpdate(UserIn, metaclass=AllOptional):
    pass


class CardID(BaseModel):
    card_id: str = Field(..., description='User card identifier')
