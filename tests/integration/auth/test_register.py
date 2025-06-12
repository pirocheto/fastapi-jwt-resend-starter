import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.factories import UserFactory
from tests.utils import fake

pytestmark = pytest.mark.anyio


@pytest.mark.integration
async def test_register_new_user(async_client: AsyncClient) -> None:
    register_data = {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": fake.password(),
    }
    response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=register_data)
    response_data = response.json()

    assert response.status_code == 201
    assert response_data["status"] == "success"
    assert response_data["code"] == "user_registered"


@pytest.mark.integration
async def test_register_existing_user(async_client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password)
    register_data = {
        "email": user.email,
        "username": user.username,
        "password": password,
    }
    response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=register_data)
    response_data = response.json()

    assert response.status_code == 409
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_already_exists"


@pytest.mark.integration
async def test_register_invalid_email(async_client: AsyncClient) -> None:
    register_data = {
        "email": "invalid-email",
        "username": fake.user_name(),
        "password": fake.password(),
    }
    response = await async_client.post(f"{settings.API_V1_STR}/auth/register", json=register_data)
    response_data = response.json()

    assert response.status_code == 422
    assert response_data["status"] == "error"
    assert response_data["code"] == "validation_error"
