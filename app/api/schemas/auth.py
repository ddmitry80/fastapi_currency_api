import datetime
import re
from typing import Annotated, Optional

from pydantic import UUID4, ConfigDict, EmailStr, Field

from app.api.schemas.custom_model import CustomModel


print(f"module {__name__} import done")

# STRONG_PASSWORD_PATTERN = r"^(?=.*[\d])(?=.*[!@#$%^&*])[\w!@#$%^&*]{6,128}$"
STRONG_PASSWORD_PATTERN = r".*"

class UserCreate(CustomModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128, pattern=STRONG_PASSWORD_PATTERN)
    is_admin: bool = False

    def to_log(self):
        return self.model_dump(mode='json', exclude_none=True, exclude=['password'])


class UserFromDB(CustomModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    email: EmailStr
    is_admin: Optional[bool] = None
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


class JWTData(CustomModel):
    user_id: int = Field(alias="sub")
    exp: datetime.datetime | None = None
    is_admin: bool = False


class AccessTokenResponse(CustomModel):
    access_token: str
    refresh_token: str


class UserRefreshTokenFromDB(CustomModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID4
    user_id: int
    refresh_token: str
    expires_at: datetime.datetime
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class UserResponse(CustomModel):
    email: EmailStr