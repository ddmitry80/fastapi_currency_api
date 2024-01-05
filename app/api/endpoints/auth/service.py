
from datetime import datetime, timedelta
import logging
import random
import string
from typing import Any
from pydantic import UUID4
import uuid

from app.api.dependencies.db import UOWDep
from app.api.endpoints.auth.config import AuthConfig, auth_config
from app.api.endpoints.auth.exceptions import InvalidCredentials
from app.api.endpoints.auth.security import check_password
from app.api.schemas.auth import UserCreate, UserFromDB, UserRefreshTokenFromDB
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork

logger = logging.getLogger(__name__)


ALPHA_NUM = string.ascii_letters + string.digits

def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


def get_refresh_token_settings(
    refresh_token: str,
    expired: bool = False,
) -> dict[str, Any]:
    base_cookie = {
        "key": auth_config.REFRESH_TOKEN_KEY,
        "httponly": True,
        "samesite": "none",
        "secure": auth_config.SECURE_COOKIES,
        # "domain": auth_config.SITE_DOMAIN,
    }
    if expired:
        return base_cookie

    return {
        **base_cookie,
        "value": refresh_token,
        "max_age": auth_config.REFRESH_TOKEN_EXP,
    }


async def create_refresh_token(
    uow: IUnitOfWork, *, user_id: int, refresh_token: str | None = None
) -> str:
    if not refresh_token:
        refresh_token = generate_random_alphanum(64)
        # refresh_token = str(uuid.uuid4())
    async with uow:
        token_data = UserRefreshTokenFromDB(
            uuid=uuid.uuid4(),
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
            user_id=user_id
        )
        token = await uow.refresh_token.add_one(token_data)
        await uow.commit()
        logger.debug(f"create_refresh_token: add token successfully")
    return refresh_token


async def get_refresh_token(uow: IUnitOfWork, refresh_token: str) -> UserRefreshTokenFromDB | None:
    async with uow:
        token = await uow.refresh_token.fetch_one(refresh_token=refresh_token)
    return token


async def expire_refresh_token(uow: IUnitOfWork, refresh_token_uuid: UUID4) -> None:
    logger.debug("expire_refresh_token: refresh_token_uuid=%s", refresh_token_uuid)
    async with uow:
        token_data = await uow.refresh_token.fetch_one(uuid=refresh_token_uuid)
        token_data.expires_at =  datetime.utcnow() - timedelta(days=1)
        token = await uow.refresh_token.update_one(token_data, uuid=refresh_token_uuid)
        await uow.commit()
        logger.debug("expire_refresh_token: token uuid=%s expired successfully", refresh_token_uuid)


async def verify_user(uow: IUnitOfWork, auth_data: UserCreate) -> UserFromDB:
    """Проверка верности пользлователя"""
    async with uow:
        user = await uow.user.verify_user(auth_data)
    if not user:
       raise InvalidCredentials() 
    logger.debug(f"verify_user: user {user.email} has got")
    return user
