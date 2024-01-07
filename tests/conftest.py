# import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from main import app, includer_routers

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


# @pytest.fixture(scope="session")
# def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "9000"
    scope = {"client": (host, port)}

    # async with TestClient(app, scope=scope) as client:
    async with AsyncClient(app=app, base_url=f"http://{host}:{port}") as ac:
        includer_routers()
        # yield client
        yield ac

