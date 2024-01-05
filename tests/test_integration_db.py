import logging

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.db.database import Base

import app.db.database

logger = logging.getLogger(__name__)

@pytest_asyncio.fixture(scope="session")
async def mock_uow() -> IUnitOfWork:
    # temp_database_uri = "sqlite:///:memory:"
    temp_database_uri = "sqlite+aiosqlite:///test_sqlite.db"
    engine = create_async_engine(temp_database_uri, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

    app.db.database.engine = engine
    app.db.database.async_session_maker = async_session_maker
    uow = UnitOfWork()
    uow.session_factory = async_session_maker
    
    # monkeypatch.setattr(src.database, "engine", engine)
    print(f"engine: init done")

    await app.db.database.init_db_schema()
    # Вставляю в БД тестовых пользователей
    await UserService.insert_test_data(uow=uow)
    # return uow
    try:
        yield uow
    finally:
        pass
        # Base.metadata.drop_all(engine, checkfirst=True)


@pytest.mark.asyncio
class TestDBIntegration:
    async def test_read_user(self, mock_uow):
        print("mock_uow type:", type(mock_uow))
        async with mock_uow:
            user = await mock_uow.user.fetch_one(id=1)
        assert user.email == "u1@example.com"
        assert user.is_admin == True
