import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


print(f"module {__name__} import done")


class AuthUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserDB(BaseModel):
    id: Optional[int]
    email: EmailStr
    

class JWTData(BaseModel):
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserResponse(BaseModel):
    email: EmailStr