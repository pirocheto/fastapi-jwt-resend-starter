import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.factories import RefreshTokenFactory, UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_refresh_token_success(async_client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password)

    # First login to get the refresh token
    login_data = {"username": user.email, "password": password}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "refresh_token" in response_data

    refresh_data = {"refresh_token": response_data["refresh_token"]}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data


async def test_refresh_token_invalid(async_client: AsyncClient) -> None:
    refresh_data = {"refresh_token": "invalid_token"}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data["status"] == "error"
    assert response_data["code"] == "refresh_token_invalid"


async def test_refresh_token_user_inactive(
    async_client: AsyncClient, user_factory: UserFactory, refresh_token_factory: RefreshTokenFactory
) -> None:
    user = await user_factory.create(is_active=False)
    db_token = await refresh_token_factory.create(user_id=user.id)

    refresh_data = {"refresh_token": db_token.token}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


async def test_refresh_token_email_not_verified(
    async_client: AsyncClient, user_factory: UserFactory, refresh_token_factory: RefreshTokenFactory
) -> None:
    user = await user_factory.create(email_verified=False)
    db_token = await refresh_token_factory.create(user_id=user.id)

    refresh_data = {"refresh_token": db_token.token}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_not_verified"
