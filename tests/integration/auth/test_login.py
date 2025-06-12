import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.factories import UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_login_success(async_client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password)

    data = {"username": user.email, "password": password}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data


async def test_login_invalid_credentials(async_client: AsyncClient, user_factory: UserFactory) -> None:
    user = await user_factory.create(password="password123")

    login_data = {"username": user.email, "password": "wrongpassword"}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data["status"] == "error"
    assert response_data["code"] == "invalid_credentials"


async def test_login_user_inactive(async_client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password, is_active=False)

    login_data = {"username": user.email, "password": password}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


async def test_login_email_not_verified(async_client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password, email_verified=False)

    login_data = {"username": user.email, "password": password}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_not_verified"
