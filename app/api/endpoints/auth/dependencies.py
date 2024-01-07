
from datetime import datetime
import logging
from typing import Annotated, Any
from fastapi import Cookie
from fastapi.params import Depends
from app.api.dependencies.db import UOWDep
from app.api.endpoints.auth.exceptions import EmailTaken, RefreshTokenNotValid
from app.api.endpoints.auth.service import get_refresh_token
from app.api.schemas.auth import UserCreate, UserFromDB, UserRefreshTokenFromDB
from app.services.user import UserService
from app.utils.unitofwork import UnitOfWork

logger = logging.getLogger(__name__)
print(f"module {__name__} import has done")


async def valid_user_create(uow: UOWDep, user: UserCreate) -> UserCreate:
    logger.debug("valid_user_create: user=%s", user.to_log())
    if await UserService.get_user(uow, email=user.email):
        raise EmailTaken()

    return user


def _is_valid_refresh_token(db_refresh_token: UserRefreshTokenFromDB) -> bool:
    return datetime.utcnow() <= db_refresh_token.expires_at


async def valid_refresh_token(
    uow: UOWDep,
    refresh_token: str = Cookie(..., alias="refreshToken"),
) -> UserRefreshTokenFromDB:
    logger.debug("valid_refresh_token: refresh_token=%s", repr(refresh_token))
    # uow = UnitOfWork()
    db_refresh_token = await get_refresh_token(uow, refresh_token)
    if not db_refresh_token:
        raise RefreshTokenNotValid()

    if not _is_valid_refresh_token(db_refresh_token):
        raise RefreshTokenNotValid()
    
    logger.debug("valid_refresh_token: return {db_refresh_token!r}")
    return db_refresh_token


async def valid_refresh_token_user(
    uow: UOWDep,
    refresh_token: Annotated[UserRefreshTokenFromDB, Depends(valid_refresh_token)],
) -> UserFromDB:
    logger.debug("valid_refresh_token_user: refresh_token=%s", repr(refresh_token))
    # uow = UnitOfWork()
    user = await UserService.get_user(uow=uow, id=refresh_token.user_id)
    if not user:
        raise RefreshTokenNotValid()
    logger.debug("valid_refresh_token_user: return user=%s", user.to_log())
    return user

