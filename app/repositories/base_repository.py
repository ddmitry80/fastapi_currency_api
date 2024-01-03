from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

from sqlalchemy import CursorResult, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[BaseModel]:
        raise NotImplementedError
    
    @abstractmethod
    async def fetch_one(self, query: dict) -> BaseModel | None:
        raise NotImplementedError


class Repository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> BaseModel:
        stmt = insert(self.model).values(**data).returning(self.model)
        data = await self.session.execute(stmt)
        res = data.scalar_one()
        return res.to_pydantic_model()

    async def find_all(self) -> list[BaseModel]:
        data = await self.session.execute(select(self.model))
        result = data.scalars().all()
        return [item.to_pydantic_model() for item in result]
    
    async def fetch_one(self, **filter_by) -> BaseModel | None:
        """Получить одну запись, по условию filter_by, или None"""
        stmt = select(self.model).where(**filter_by)
        data = await self.session.execute(stmt)
        result = data.scalar_one_or_none()
        return result.to_pydantic_model() if result is not None else None
    
    async def update_one(self, data: dict, **where) -> BaseModel:
        """Обновляет одну запись данными из data, по условию where. Если запись не одна, вызывается исключение"""
        stmt = update(self.model).values(**data).where(**where).returning(self.model)
        data: CursorResult = await self.session.execute(stmt)
        result = data.scalar_one()
        return result.to_pydantic_model()

