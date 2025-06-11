import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.factories import PasswordResetTokenFactory, UserFactory
from tests.utils import fake


@pytest.mark.integration
def test_send_email_reset_password(client: TestClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = user_factory.create(password=password)

    reset_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/password/forgot", json=reset_data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "password_reset_link_sent"


@pytest.mark.integration
def test_send_email_reset_password_user_inactive(client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(is_active=False)

    reset_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/password/forgot", json=reset_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
def test_send_email_reset_password_user_not_found(client: TestClient) -> None:
    reset_data = {"email": fake.email()}
    response = client.post(f"{settings.API_V1_STR}/auth/password/forgot", json=reset_data)
    response_data = response.json()

    assert response.status_code == 404
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_not_found"


@pytest.mark.integration
def test_send_email_reset_password_invalid_email(client: TestClient) -> None:
    reset_data = {"email": "invalid-email"}
    response = client.post(f"{settings.API_V1_STR}/auth/password/forgot", json=reset_data)
    response_data = response.json()

    assert response.status_code == 422
    assert response_data["status"] == "error"
    assert response_data["code"] == "validation_error"


@pytest.mark.integration
def test_reset_password_with_link(
    session: Session,
    client: TestClient,
    user_factory: UserFactory,
    password_reset_token_factory: PasswordResetTokenFactory,
) -> None:
    user = user_factory.create()
    db_token = password_reset_token_factory.create(user_id=user.id)

    update_data = {"token": db_token.token, "new_password": fake.password()}
    response = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=update_data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "password_updated"


@pytest.mark.integration
def test_reset_password_with_invalid_link(client: TestClient) -> None:
    update_data = {"token": "invalid_token", "new_password": fake.password()}
    response = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=update_data)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "password_reset_token_invalid"


@pytest.mark.integration
def test_reset_password_with_used_link(
    session: Session,
    client: TestClient,
    user_factory: UserFactory,
    password_reset_token_factory: PasswordResetTokenFactory,
) -> None:
    user = user_factory.create()
    db_token = password_reset_token_factory.create(user_id=user.id, used=True)

    update_data = {"token": db_token.token, "new_password": fake.password()}
    response = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=update_data)
    response_data = response.json()
    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "password_reset_token_already_used"


@pytest.mark.integration
def test_reset_password_with_inactive_user(
    session: Session,
    client: TestClient,
    user_factory: UserFactory,
    password_reset_token_factory: PasswordResetTokenFactory,
) -> None:
    user = user_factory.create(is_active=False)
    db_token = password_reset_token_factory.create(user_id=user.id)

    update_data = {"token": db_token.token, "new_password": fake.password()}
    response = client.post(f"{settings.API_V1_STR}/auth/password/reset", json=update_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"
