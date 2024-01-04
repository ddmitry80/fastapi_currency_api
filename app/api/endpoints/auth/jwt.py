from datetime import datetime, timedelta
from typing import Annotated, Any, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.api.endpoints.auth.config import AuthConfig, auth_config
# from jose import JWTError, jwt
import jwt

# from src.auth.config import auth_config
from app.api.endpoints.auth.exceptions import AuthorizationFailed, AuthRequired, InvalidToken
from app.api.schemas.auth import JWTData, UserFromDB
from app.core.config import settings
from app.services.user import UserService
# from src.auth.service import get_user_by_id

print(f"module {__name__} import done")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/tokens", auto_error=False)


def create_access_token(
    *,
    user: dict[str, Any],
    expires_delta: timedelta = timedelta(minutes=auth_config.JWT_EXP),
) -> str:
    jwt_data = {
        "sub": str(user["user_id"]),
        "exp": datetime.utcnow() + expires_delta,
        "is_admin": user["is_admin"],
    }
    return jwt.encode(payload=jwt_data, key=auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)


async def parse_jwt_user_data_optional(token: Annotated[str, Depends(oauth2_scheme)]) -> JWTData | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, auth_config.JWT_SECRET, algorithms=[auth_config.JWT_ALG])
    except jwt.exceptions.PyJWTError:
        raise InvalidToken()
    return JWTData(**payload)


async def parse_jwt_user_data(
    token: Annotated[Optional[JWTData], Depends(parse_jwt_user_data_optional)],
) -> JWTData:
    if not token:
        raise AuthRequired()
    return token


async def parse_jwt_admin_data(token: Annotated[JWTData, Depends(parse_jwt_user_data)]) -> JWTData:
    if not token.is_admin:
        raise AuthorizationFailed()
    return token


async def validate_admin_access(
        token: Annotated[Optional[JWTData], Depends(parse_jwt_user_data_optional)],
) -> None:
    if not token or not token.is_admin:
        raise AuthorizationFailed()
    return


async def get_current_user(jwt_data: Annotated[JWTData, Depends(parse_jwt_user_data)]) -> UserFromDB:
    user = await UserService.get_user(id=jwt_data.user_id)
    return user
