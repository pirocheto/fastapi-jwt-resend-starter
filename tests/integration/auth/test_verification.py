import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import EmailVerificationToken
from tests.factories import EmailVerificationTokenFactory, UserFactory
from tests.utils import fake


@pytest.mark.integration
def test_confirm_email_success(
    client: TestClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = user_factory.create(email_verified=False)
    db_token = email_verification_token_factory.create(user_id=user.id)

    params = {"token": db_token.token}
    response = client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "user_verified"


@pytest.mark.integration
def test_confirm_email_invalid_token(client: TestClient) -> None:
    params = {"token": "invalid_token"}
    response = client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "verification_token_invalid"


@pytest.mark.integration
def test_confirm_email_used_token(
    session: Session,
    client: TestClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = user_factory.create(email_verified=False)
    db_token = email_verification_token_factory.create(user_id=user.id, used=True)

    params = {"token": db_token.token}
    response = client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "verification_token_already_used"


@pytest.mark.integration
def test_confirm_email_already_verified(
    session: Session,
    client: TestClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = user_factory.create(email_verified=True)
    db_token = email_verification_token_factory.create(user_id=user.id)

    params = {"token": db_token.token}
    response = client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_already_verified"


@pytest.mark.integration
def test_confirm_email_inactive_user(session: Session, client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(is_active=False)

    # Create an email verification token for the inactive user
    token_data = {
        "token": fake.uuid4(),
        "user_id": user.id,
        "expires_at": fake.future_datetime(end_date="+1d"),
        "used": False,
    }
    email_verification_token = EmailVerificationToken(**token_data)
    user.email_verification_tokens.append(email_verification_token)

    session.add(user)
    session.commit()

    params = {"token": email_verification_token.token}
    response = client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
def test_resend_verification_email_success(client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(email_verified=False)

    resend_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "verification_email_sent"


@pytest.mark.integration
def test_resend_verification_email_user_inactive(client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(is_active=False)

    resend_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
def test_resend_verification_email_already_verified(client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(email_verified=True)

    resend_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_already_verified"
