from abc import ABC, abstractmethod
import logging
from typing import Type

from app.db.database import async_session_maker
from app.repositories.user_repository import UserRefreshTokenRepository, UserRepository

logger = logging.getLogger(__name__)

class IUnitOfWork(ABC):
    user: Type[UserRepository]
    refresh_token: Type[UserRefreshTokenRepository]

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        logger.debug("begin uow context manager")
        self.session = self.session_factory()

        self.user = UserRepository(self.session)
        self.refresh_token = UserRefreshTokenRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
