from abc import abstractmethod
from sqlalchemy import LargeBinary
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(settings.ASYNC_DATABASE_URL)  # создали движок БД
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)  # передали наш движок в создатель сессий


class Base(DeclarativeBase):
    def __str__(self) -> str:
        excludes = [LargeBinary, ]
        attrs = (f'{c.name!r}: {repr(getattr(self, c.name)) if c.type not in [excludes] else repr("***")}' for c in self.__table__.columns)
        return ', '.join(attrs)
    
    def __repr__(self) -> str:
        excludes = [LargeBinary, ]
        attrs = (f'{c.name!r}: {getattr(self, c.name)!r}' for c in self.__table__.columns if c.type not in [excludes])
        return f"{self.__class__.__name__}({', '.join(attrs)})"
    
    def as_dict(self) -> dict:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    @abstractmethod
    def to_pydantic_model(self):
        raise NotImplementedError


async def get_async_session():
    async with async_session_maker() as session:
        yield session

