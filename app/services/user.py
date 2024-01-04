import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
import logging

from pydantic import UUID4
from sqlalchemy import insert, select, update
from app.api.dependencies.db import UOWDep
from app.api.endpoints.auth.config import AuthConfig
from app.api.endpoints.auth.exceptions import InvalidCredentials

from app.api.endpoints.auth.security import check_password, hash_password
from app.api.schemas.auth import UserCreate, UserFromDB
from app.db.models import User
from app.utils.unitofwork import IUnitOfWork

# from src import utils
# from src.auth.config import auth_config
# from src.auth.exceptions import InvalidCredentials
# from src.auth.schemas import AuthUser
# from src.auth.security import check_password, hash_password
# from src.database import User, Token, execute, fetch_one

logger = logging.getLogger(__name__)
print(f"module {__name__} import done")

class UserService:
    @staticmethod
    async def create_user(user: UserCreate, uow: IUnitOfWork) -> UserFromDB | None:
        """Создать пользователя в БД"""
        async with uow:
            user = await uow.user.add_one({'email': user.email, 'password': hash_password(user.password)})
        return user

    @staticmethod
    async def get_user(uow: IUnitOfWork, id: Optional[str] = None, email: Optional[str] = None) -> UserFromDB | None:
        """Найти пользователя в БД по id или по email"""
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
    async def insert_mock_data(uow: IUnitOfWork):
        user1 = User(email='u1@example.com', password=hash_password('Aa1234!'), is_admin=True)
        user2 = User(email='u2@example.com', password=hash_password('Aa1234!'))
        print(f"create_ddl: before engine")
        # async with AsyncSession(engine) as session, session.begin():
        #     session.add_all((prod1, prod2, user1, user2))
        async with uow:
            uow.user.add_one(user1.as_dict())
            uow.user.add_one(user2.as_dict())
            uow.commit()
        return None

