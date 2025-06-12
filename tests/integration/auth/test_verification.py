import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import EmailVerificationToken
from tests.factories import EmailVerificationTokenFactory, UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_confirm_email_success(
    async_client: AsyncClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = await user_factory.create(email_verified=False)
    db_token = await email_verification_token_factory.create(user_id=user.id)

    params = {"token": db_token.token}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "user_verified"


@pytest.mark.integration
async def test_confirm_email_invalid_token(async_client: AsyncClient) -> None:
    params = {"token": "invalid_token"}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "verification_token_invalid"


@pytest.mark.integration
async def test_confirm_email_used_token(
    async_session: Session,
    async_client: AsyncClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = await user_factory.create(email_verified=False)
    db_token = await email_verification_token_factory.create(user_id=user.id, used=True)

    params = {"token": db_token.token}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "verification_token_already_used"


@pytest.mark.integration
async def test_confirm_email_already_verified(
    async_session: Session,
    async_client: AsyncClient,
    user_factory: UserFactory,
    email_verification_token_factory: EmailVerificationTokenFactory,
) -> None:
    user = await user_factory.create(email_verified=True)
    db_token = await email_verification_token_factory.create(user_id=user.id)

    params = {"token": db_token.token}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_already_verified"


@pytest.mark.integration
async def test_confirm_email_inactive_user(
    async_session: Session, async_client: AsyncClient, user_factory: UserFactory
) -> None:
    user = await user_factory.create(is_active=False)

    # Create an email verification token for the inactive user
    token_data = {
        "token": fake.uuid4(),
        "user_id": user.id,
        "expires_at": fake.future_datetime(end_date="+1d"),
        "used": False,
    }
    email_verification_token = EmailVerificationToken(**token_data)
    user.email_verification_tokens.append(email_verification_token)

    async_session.add(user)
    async_session.commit()

    params = {"token": email_verification_token.token}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/verify-email", params=params)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
async def test_resend_verification_email_success(async_client: AsyncClient, user_factory: UserFactory) -> None:
    user = await user_factory.create(email_verified=False)

    resend_data = {"email": user.email}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "verification_email_sent"


@pytest.mark.integration
async def test_resend_verification_email_user_inactive(async_client: AsyncClient, user_factory: UserFactory) -> None:
    user = await user_factory.create(is_active=False)

    resend_data = {"email": user.email}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
async def test_resend_verification_email_already_verified(
    async_client: AsyncClient, user_factory: UserFactory
) -> None:
    user = await user_factory.create(email_verified=True)

    resend_data = {"email": user.email}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/resend-verification", json=resend_data)
    response_data = response.json()

    assert response.status_code == 400
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_already_verified"
