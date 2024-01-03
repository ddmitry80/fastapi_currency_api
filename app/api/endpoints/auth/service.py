
from datetime import datetime, timedelta
import logging
from typing import Any
from pydantic import UUID4
import uuid

from app.api.dependencies.db import UOWDep
from app.api.endpoints.auth.config import AuthConfig, auth_config
from app.api.endpoints.auth.exceptions import InvalidCredentials
from app.api.endpoints.auth.security import check_password
from app.api.schemas.auth import UserCreate, UserFromDB, UserRefreshTokenFromDB
from app.services.user import UserService

logger = logging.getLogger(__name__)

def get_refresh_token_settings(
    refresh_token: str,
    expired: bool = False,
) -> dict[str, Any]:
    base_cookie = {
        "key": auth_config.REFRESH_TOKEN_KEY,
        "httponly": True,
        "samesite": "none",
        "secure": auth_config.SECURE_COOKIES,
        "domain": auth_config.SITE_DOMAIN,
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": auth_config.REFRESH_TOKEN_EXP,
    }


async def create_refresh_token(
    uow: UOWDep, *, user_id: int, refresh_token: str | None = None
) -> str:
    if not refresh_token:
        # refresh_token = utils.generate_random_alphanum(64)
        refresh_token = uuid.uuid4().__str__()
    async with uow:
        token = await uow.refresh_token.add_one({
            "uuid": uuid.uuid4(),
            "refresh_token": refresh_token,
            "expires_at": datetime.utcnow() + timedelta(seconds=AuthConfig.REFRESH_TOKEN_EXP),
            "user_id": user_id,
        })
        uow.commit()
        logger.debug(f"create_refresh_token: add token successfully")
    return refresh_token


async def get_refresh_token(uow: UOWDep, refresh_token: str) -> UserRefreshTokenFromDB | None:
    async with uow:
        token = await uow.refresh_token.fetch_one(refresh_token=refresh_token)
    return token


async def expire_refresh_token(uow: UOWDep, refresh_token_uuid: UUID4) -> None:
    async with uow:
        token = await uow.refresh_token.update_one(
            data={"expires_at": datetime.utcnow() - timedelta(days=1)}, 
            uuid=refresh_token_uuid
            )
        uow.commit()
        logger.debug(f"expire_refresh_token: token expired successfully")


async def authenticate_user(auth_data: UserCreate, uow: UOWDep) -> UserFromDB:
    async with uow:
        user = await uow.user.verify_user(auth_data)
    if not user:
       raise InvalidCredentials() 
    logger.debug(f"authentificate_user: user {user.email} has got")
    return user
