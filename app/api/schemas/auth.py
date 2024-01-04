import datetime
import re
from typing import Annotated, Optional

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field


print(f"module {__name__} import done")

# STRONG_PASSWORD_PATTERN = r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$"
# STRONG_PASSWORD_PATTERN = r"^[a-zA-Z\d]+$"
STRONG_PASSWORD_PATTERN = r".*"

class UserCreate(BaseModel):
    email: EmailStr
    # password: Annotated[str, StringConstraints(min_length=6, max_length=128, strip_whitespace=True, pattern=STRONG_PASSWORD_PATTERN)]
    password: str = Field(min_length=6, max_length=128, pattern=STRONG_PASSWORD_PATTERN)
    is_admin: bool = False


class UserFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    email: EmailStr
    is_admin: Optional[bool] = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
 
    def to_log(self):
        return self.model_dump(mode='json', exclude_none=True)


class JWTData(BaseModel):
    user_id: int = Field(alias="sub")
    is_admin: bool = False


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserRefreshTokenFromDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID4
    user_id: int
    refresh_token: str
    expires_at: datetime.datetime
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    def to_log(self):
        return self.model_dump(mode='json', exclude_none=True)


class UserResponse(BaseModel):
    email: EmailStr