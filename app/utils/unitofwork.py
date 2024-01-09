from abc import ABC, abstractmethod
import logging
from typing import Type

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
        logger.debug("UnitOfWork: begin context manager, current level=%s", self._hierarchy)
        if self.session is None:
            self.session = self.session_factory()
        self._hierarchy += 1
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
        logger.debug("UnitOfWork: commit")
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
