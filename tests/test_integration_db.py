import logging
from logging import config as logging_config
from httpx import AsyncClient
from pydantic import ConfigDict 
from fastapi import status

from sqlalchemy import NullPool
from app.api.schemas.auth import UserCreate

logging_config.fileConfig('logging.ini')

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.services.user import UserService
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.config import settings, Settings
from app.db.database import Base

import app.db.database

logger = logging.getLogger(__name__)

# pytestmark = pytest.mark.anyio

@pytest.fixture(scope="session")
async def env_file(monkeypatch):
    mock_settings = Settings(_env_file=".test.env")
    settings = mock_settings
    print("mock_settings DB_NAME:", mock_settings.DB_NAME)

    monkeypatch.setattr(app.core.config, "settings", mock_settings)
    monkeypatch.setattr(app.db.database, "settings", mock_settings)
    print("DB_NAME:", settings.DB_NAME)
    return settings


@pytest.fixture(scope="session")
async def async_db_sesstion():
    if settings.MODE == 'TEST':
        engine_uri = settings.ASYNC_DATABASE_URL
        # engine = create_async_engine(engine_uri, echo=True, poolclass=NullPool)
        engine = create_async_engine(engine_uri, echo=True)
        async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

        app.db.database.engine = engine
        app.db.database.async_session_maker = async_session_maker

        await app.db.database.init_db_schema()
        print(f"async_db_sesstion: init db schema done")

        yield async_session_maker
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    else:
        raise ValueError("Настройки не в TEST режиме: смотри .env и .test.env")



@pytest.fixture(scope="session")
async def mock_uow(async_db_sesstion) -> UnitOfWork:

    uow = UnitOfWork()
    uow.session_factory = async_db_sesstion

    print(f"UnitOfWork: init done")

    # Вставляю в БД тестовых пользователей
    async with uow:
        await UserService.insert_test_data(uow=uow)
        yield uow


@pytest.mark.anyio
class TestDBIntegration:
    async def test_read_user(self, mock_uow: UnitOfWork, client: AsyncClient):
        user = await mock_uow.user.fetch_one(id=1)
        assert user.email == "u1@example.com"
        assert user.is_admin == True

    async def test_create_user(self, mock_uow: UnitOfWork, client: AsyncClient):
        new_user = UserCreate(email="test@example.com", password="A12345a!")

        response = await client.post('/auth/users', json=new_user.model_dump())
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == new_user.email

    async def test_login(self, mock_uow: UnitOfWork, client: AsyncClient):
        auth_body = {"username": "u2@example.com", "password": "Aa1234!", "grant_type": "password"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = await client.post("/auth/users/tokens", data=auth_body, headers=headers)
        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert response.json()["refresh_token"] is not None
