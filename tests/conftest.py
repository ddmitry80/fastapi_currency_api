# import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.database import Base
import app.db.database
from app.services.user_service import UserService
from app.utils.unitofwork import UnitOfWork

# from main import app, includer_routers
from main import includer_routers

# @pytest.fixture(autouse=True, scope="session")
# def run_migrations() -> None:
#     import os
#     print("running migrations..")
#     os.system("alembic upgrade head")
#     yield
#     os.system("alembic downgrade base")

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio", {"use_uvloop": True}



@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    from main import app

    host, port = "127.0.0.1", "9000"

    async with AsyncClient(app=app, base_url=f"http://{host}:{port}") as ac:
        includer_routers()
        yield ac


@pytest.fixture(scope="session")
async def async_db_sesstion():
    if settings.MODE != 'TEST':
        raise ValueError("Настройки не в TEST режиме: смотри .env и .test.env")
    # engine_uri = settings.ASYNC_DATABASE_URL
    # # engine = create_async_engine(engine_uri, echo=True, poolclass=NullPool)
    # engine = create_async_engine(engine_uri, echo=True)
    # async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

    # app.db.database.engine = engine
    # app.db.database.async_session_maker = async_session_maker
    # from app.db.database import async_session_maker
    import app.db.database
    from app.db.database import async_session_maker

    await app.db.database.init_db_schema()
    print(f"async_db_sesstion: init db schema done")

    yield async_session_maker

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    # await engine.dispose()
        


@pytest.fixture(scope="session")
async def with_uow(async_db_sesstion) -> UnitOfWork:

    uow = UnitOfWork()
    uow.session_factory = async_db_sesstion

    print(f"UnitOfWork: init done")
    async with uow:
        yield uow


@pytest.fixture(scope="session", autouse=True)
async def add_users(with_uow):
    uow = with_uow

    await UserService.insert_test_data(uow=uow)
    await uow.commit()
