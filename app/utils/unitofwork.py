from abc import ABC, abstractmethod
import logging
from typing import Type
import sqlalchemy.exc

from app.db.database import async_session_maker
from app.repositories.currency_repository import CurrencyRepository
from app.repositories.rate_repository import RateRepository
from app.repositories.user_repository import UserRefreshTokenRepository, UserRepository

logger = logging.getLogger(__name__)

class IUnitOfWork(ABC):
    user: Type[UserRepository]
    refresh_token: Type[UserRefreshTokenRepository]
    currency: Type[CurrencyRepository]
    rate: Type[RateRepository]

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
        self._hierarchy = 0
        self.session = None

    def _init_repositories(self):
        self.user = UserRepository(self.session)
        self.refresh_token = UserRefreshTokenRepository(self.session)
        self.currency = CurrencyRepository(self.session)
        self.rate = RateRepository(self.session)

    async def __aenter__(self):
        if self.session is None:
            self.session = self.session_factory()
        self._hierarchy += 1
        logger.debug("UnitOfWork: begin context manager, level=%s", self._hierarchy)
        self._init_repositories()

    async def __aexit__(self, *args):
        logger.debug("UnitOfWork: exit context manager, current level=%s", self._hierarchy)
        await self.rollback()
        self._hierarchy -= 1
        if self._hierarchy == 0:
            await self.session.close()
            self.session = None
        self._init_repositories()

    async def commit(self):
        if self._hierarchy == 1:
            logger.debug("UnitOfWork: commit called at level=1, do commit")
            await self.session.commit()
        elif self._hierarchy > 1:
            # await self.session.refresh()
            logger.debug("UnitOfWork: commit called at level=%s, do nothing", self._hierarchy)
        else:
            raise sqlalchemy.exc.InterfaceError("UnitOfWork: Попытка вызова commit без контекста")

    async def rollback(self):
        if self._hierarchy == 1:
            logger.debug("UnitOfWork: rollback calldd at level=1, do rollback")
            await self.session.rollback()
        else:
            logger.debug("UnitOfWork: rollback calldd at level=%s, do nothing", self._hierarchy)
