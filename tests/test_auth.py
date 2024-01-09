import logging
import pytest

from httpx import AsyncClient
from fastapi import status
# from sqlalchemy import NullPool

from app.api.schemas.auth import UserCreate
from app.utils.unitofwork import IUnitOfWork, UnitOfWork
from app.core.config import Settings
# import app.db.database


logger = logging.getLogger(__name__)

# pytestmark = pytest.mark.anyio

# @pytest.fixture(scope="session")
# async def env_file(monkeypatch):
#     mock_settings = Settings(_env_file=".test.env")
#     settings = mock_settings
#     print("mock_settings DB_NAME:", mock_settings.DB_NAME)

#     monkeypatch.setattr(app.core.config, "settings", mock_settings)
#     monkeypatch.setattr(app.db.database, "settings", mock_settings)
#     print("DB_NAME:", settings.DB_NAME)
#     return settings


@pytest.mark.anyio
class TestDBIntegration:
    async def test_read_user(self, with_uow: UnitOfWork, client: AsyncClient):
        user = await with_uow.user.fetch_one(id=1)
        assert user.email == "u1@example.com"
        assert user.is_admin == True

    async def test_create_user(self, with_uow: UnitOfWork, client: AsyncClient):
        new_user = UserCreate(email="test@example.com", password="A12345a!")

        response = await client.post('/auth/users', json=new_user.model_dump())
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == new_user.email

    async def test_login(self, with_uow: UnitOfWork, client: AsyncClient):
        auth_body = {"username": "u2@example.com", "password": "Aa1234!", "grant_type": "password"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = await client.post("/auth/users/tokens", data=auth_body, headers=headers)
        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert response.json()["refresh_token"] is not None

    
    async def test_bad_login(self, with_uow: UnitOfWork, client: AsyncClient):
        auth_body = {"username": "u_xxx@example.com", "password": "Aa1234!", "grant_type": "password"}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = await client.post("/auth/users/tokens", data=auth_body, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
