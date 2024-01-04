import logging
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import insert, select
from app.api.endpoints.auth.security import check_password, hash_password
from app.api.schemas.auth import UserCreate, UserFromDB
from app.repositories.base_repository import Repository, AbstractRepository
from app.db.models import User, UserRefreshToken

logger = logging.getLogger(__name__)


class UserRepository(Repository):
    model = User

    async def verify_user(self, user: UserCreate) -> Optional[UserFromDB]:
        """Проверка совпадения имени пользователя/пароля. Возвращает данные пользователя из БД"""
        stmt = select(self.model).where(email=user.email)
        db_data = await self.session.execute(stmt)
        db_user: User = db_data.scalar_one_or_none()
        if not db_user or not check_password(user.password, db_user["password"]):
            return None
        return db_user.to_pydantic_model()
    
    async def add_one(self, data: UserCreate) -> BaseModel:
        logger.debug(f"add_one: {data.email=}, {data.is_admin=}")
        email, password, is_admin = data.email, hash_password(data.password), data.is_admin
        stmt = insert(self.model).values(email=email, password=password, is_admin=is_admin).returning(self.model)
        data = await self.session.execute(stmt)
        res = data.scalar_one()
        return res.to_pydantic_model()


class UserRefreshTokenRepository(Repository):
    model = UserRefreshToken
