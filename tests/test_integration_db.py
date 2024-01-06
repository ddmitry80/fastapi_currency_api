import logging
from logging import config as logging_config
from httpx import AsyncClient
from pydantic import ConfigDict

from sqlalchemy import NullPool
from app.api.schemas.auth import UserCreate

logging_config.fileConfig('logging.ini')

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.config import settings, Settings
from app.db.database import Base

import app.db.database

logger = logging.getLogger(__name__)

# @pytest_asyncio.fixture(scope="session")
@pytest_asyncio.fixture
async def env_file(monkeypatch):
    # class MockSettings(Settings):
    #     model_config = ConfigDict(
    #         env_file=".test.env", 
    #         env_file_encoding="utf-8", 
    #         extra="ignore",
    #         )
        
    mock_settings = Settings(_env_file=".test.env")
    settings = mock_settings
    print("mock_settings DB_NAME:", mock_settings.DB_NAME)

    monkeypatch.setattr(app.core.config, "settings", mock_settings)
    monkeypatch.setattr(app.db.database, "settings", mock_settings)
    print("DB_NAME:", settings.DB_NAME)
    return settings


# @pytest_asyncio.fixture(scope="session")
@pytest_asyncio.fixture
async def async_db_sesstion(env_file):
    # temp_database_uri = "postgresql+asyncpg://postgres:postgres@localhost:5433/test"
    # engine = create_async_engine(temp_database_uri, echo=True, poolclass=NullPool)
    # async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
    engine_uri = env_file.ASYNC_DATABASE_URL
    engine = create_async_engine(engine_uri, echo=True, poolclass=NullPool)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

    app.db.database.engine = engine
    app.db.database.async_session_maker = async_session_maker

    await app.db.database.init_db_schema()
    print(f"async_db_sesstion: init db schema done")

    yield async_session_maker
    # Base.metadata.drop_all(engine, checkfirst=True)


# @pytest.mark.anyio
@pytest_asyncio.fixture()
async def mock_uow(async_db_sesstion) -> UnitOfWork:

    uow = UnitOfWork(session_factory=async_db_sesstion)

    print(f"UnitOfWork: init done")

    # Вставляю в БД тестовых пользователей
    async with uow:
        await UserService.insert_test_data(uow=uow)
        yield uow


@pytest.mark.asyncio
class TestDBIntegration:
    async def test_read_user(self, mock_uow, client):
        # print("mock_uow type:", type(mock_uow))
        # async with mock_uow:
        user = await mock_uow.user.fetch_one(id=1)
        assert user.email == "u1@example.com"
        assert user.is_admin == True

    async def test_create_user(self, mock_uow: UnitOfWork, client: AsyncClient):
        new_user = UserCreate(email="test@example.com", password="A12345a!")
        response = await client.post('/auth/users', json=new_user.to_log())
        assert response.json()["email"] == new_user.email
