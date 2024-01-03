import datetime
import re
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


print(f"module {__name__} import done")

# STRONG_PASSWORD_PATTERN = r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$"
STRONG_PASSWORD_PATTERN = r"^[a-zA-Z\d]+$"

class UserCreate(BaseModel):
    email: EmailStr
    # password: Annotated[str, StringConstraints(min_length=6, max_length=128, strip_whitespace=True, pattern=STRONG_PASSWORD_PATTERN)]
    password: str = Field(min_length=6, max_length=128, pattern=STRONG_PASSWORD_PATTERN)
    is_admin: bool = False


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


# class UserResponse(BaseModel):
#     email: EmailStr