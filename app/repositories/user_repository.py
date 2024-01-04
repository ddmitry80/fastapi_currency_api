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
        logger.debug(f"verify_user: {user!r}")
        stmt = select(self.model).filter_by(email=user.email)
        db_data = await self.session.execute(stmt)
        db_user: User = db_data.scalar_one_or_none()
        if not db_user or not check_password(user.password, db_user.password):
            logger.debug(f"verify_user: user {user.email} has not verified")
            return None
        result = db_user.to_pydantic_model()
        logger.debug(f"verify_user: user=%s has verified", result.to_log())
        return result
    
    async def add_one(self, data: UserCreate) -> UserFromDB:
        """Создание пользователя. Принимает пароль в открытов виде, в БД сохраняет хэш. Возвращает модель Pydentic пользователя"""
        logger.debug(f"add_one: {data.email=}, {data.is_admin=}")
        email, password, is_admin = data.email, hash_password(data.password), data.is_admin
        stmt = insert(self.model).values(email=email, password=password, is_admin=is_admin).returning(self.model)
        data = await self.session.execute(stmt)
        result = data.scalar_one().to_pydantic_model()
        logger.debug(f"update_one: result={result.to_log()}")
        return result


class UserRefreshTokenRepository(Repository):
    model = UserRefreshToken
