from abc import ABC, abstractmethod
import logging
from typing import Any
from pydantic import BaseModel

from sqlalchemy import CursorResult, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import CustomModel

logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: BaseModel) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[BaseModel]:
        raise NotImplementedError
    
    @abstractmethod
    async def fetch_one(self, **filter_by: dict) -> BaseModel | None:
        raise NotImplementedError
    
    @abstractmethod
    async def update_one(self, data: BaseModel, **where: dict) -> BaseModel:
        raise NotImplementedError


class Repository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: CustomModel) -> BaseModel:
        """Добавить одну запись в БД (модель Pydentic)"""
        logger.debug(f"add_one: data={data.to_log()}")
        stmt = insert(self.model).values(**data.model_dump(exclude_none=True)).returning(self.model)
        data = await self.session.execute(stmt)
        res = data.scalar_one()
        return res.to_pydantic_model()

    async def find_all(self) -> list[BaseModel]:
        """Получить все записи из таблицы в БД, списком"""
        logger.debug("find_all")
        data = await self.session.execute(select(self.model))
        result = data.scalars().all()
        return [item.to_pydantic_model() for item in result]
    
    async def fetch_one(self, **filter_by: dict) -> BaseModel | None:
        """Получить одну запись, по условию filter_by, или None"""
        logger.debug(f"fetch_one: {filter_by=}")
        stmt = select(self.model).filter_by(**filter_by)
        data = (await self.session.execute(stmt)).scalar_one_or_none()
        result = data.to_pydantic_model() if data is not None else None
        logger.debug(f"fetch_one: result={result.to_log()}")
        return result
    
    async def update_one(self, data: BaseModel, **where: dict) -> BaseModel:
        """Обновляет одну запись данными из data, по условию where. Если запись не одна, вызывается исключение"""
        logger.debug(f"update_one: {data=}, {where=}")
        stmt = update(self.model).values(**data.model_dump(exclude_none=True)).where(**where).returning(self.model)
        data: CursorResult = await self.session.execute(stmt)
        result = data.scalar_one().to_pydantic_model()
        logger.debug(f"update_one: result={result.to_log()}")
        return result

