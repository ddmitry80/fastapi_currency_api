import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
import logging

from pydantic import UUID4
from sqlalchemy import insert, select, update
from app.api.dependencies.db import UOWDep
from app.auth.config import AuthConfig
from app.auth.exceptions import InvalidCredentials

from app.auth.security import check_password, hash_password
from app.api.schemas.auth import UserCreate, UserFromDB
from app.db.models import User
from app.utils.unitofwork import IUnitOfWork


logger = logging.getLogger(__name__)
print(f"module {__name__} import done")

class UserService:
    @staticmethod
    async def create_user(uow: IUnitOfWork, user: UserCreate) -> UserFromDB | None:
        """Создать пользователя в БД"""
        logger.debug("create_user: user=%s", user.to_log())
        async with uow:
            user = await uow.user.add_one(user)
            await uow.commit()
        logger.info(f"create_user: user={user.to_log()}")
        return user

    @staticmethod
    async def get_user(uow: IUnitOfWork, id: Optional[str] = None, email: Optional[str] = None) -> UserFromDB | None:
        """Найти пользователя в БД по id или по email"""
        logger.debug("get_user: id=%s, email=%s", id, email)
        async with uow:
            filter_by = {}
            if id: 
                filter_by['id'] = id
            elif email:
                filter_by['email'] = email
            else:
                raise ValueError("Не указаны ни поле 'id', ни поле 'email'")
            user = await uow.user.fetch_one(**filter_by)
        return user
    
    @staticmethod
    async def insert_test_data(uow: IUnitOfWork):
        """Создает тестовые данные пользователя в БД"""
        logger.debug("insert_test_data")
        user1 = UserCreate(email='u1@example.com', password='Aa1234!', is_admin=True)
        user2 = UserCreate(email='u2@example.com', password='Aa1234!')        
        async with uow:
            logger.debug(f"insert_mock_data: before insert data")
            await uow.user.add_one(user1)
            await uow.user.add_one(user2)
            await uow.commit()
        return None

