import datetime
import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


print(f"module {__name__} import done")


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    email: EmailStr
    is_admin: Optional[bool]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    

class JWTData(BaseModel):
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    email: EmailStr