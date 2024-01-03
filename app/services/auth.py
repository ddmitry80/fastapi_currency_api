import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
import logging

from pydantic import UUID4
from sqlalchemy import insert, select, update
from app.api.dependencies.db import UOWDep
from app.api.endpoints.auth.exceptions import InvalidCredentials

from app.api.endpoints.auth.security import check_password, hash_password
from app.api.schemas.auth import UserCreate, UserFromDB
from app.db.models import User

# from src import utils
# from src.auth.config import auth_config
# from src.auth.exceptions import InvalidCredentials
# from src.auth.schemas import AuthUser
# from src.auth.security import check_password, hash_password
# from src.database import User, Token, execute, fetch_one

logger = logging.getLogger(__name__)
print(f"module {__name__} import done")

class UserService:
    async def create_user(user: UserCreate, uow: UOWDep) -> UserFromDB | None:
        async with uow:
            user = await uow.user.add_one({'email': user.email, 'password': hash_password(user.password)})
        return user


    async def get_user_by_id(user_id: int, uow: UOWDep) -> Optional[UserFromDB]:
        async with uow:
            user = await uow.user.find_one(user_id=user_id)
        return user


    async def get_user_by_email(email: str, uow: UOWDep) -> dict[str, Any] | None:
        async with uow:
            user = await uow.user.find_one(email=email)
        return user


    async def create_refresh_token(
        *, user_id: int, refresh_token: str | None = None
    ) -> str:
        if not refresh_token:
            refresh_token = utils.generate_random_alphanum(64)

        insert_query = insert(Token).values(
            uuid=uuid.uuid4(),
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
            user_id=user_id,
        )
        await execute(insert_query)

        return refresh_token


    # async def get_refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
    #     select_query = select(Token).where(Token.refresh_token == refresh_token)
    #     return await fetch_one(select_query)


    async def expire_refresh_token(self, refresh_token_uuid: UUID4) -> None:
        update_query = (
            update(Token)
            .values(expires_at=datetime.utcnow() - timedelta(days=1))
            .where(Token.c.uuid == refresh_token_uuid)
        )

        await execute(update_query)


    async def authenticate_user(self, auth_data: UserCreate) -> UserFromDB:
        user = await self.get_user_by_email(auth_data.email)
        if not user:
            raise InvalidCredentials()

        if not check_password(auth_data.password, user["password"]):
            raise InvalidCredentials()

        return user
