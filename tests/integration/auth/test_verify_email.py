import pytest
from httpx import AsyncClient

from tests.factories import UserFactory, VerificationTokenFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_verify_email_success(
    client: AsyncClient, user_factory: UserFactory, verif_token_factory: VerificationTokenFactory
) -> None:
    token = fake.uuid4()
    user = await user_factory.create()

    await verif_token_factory.create(user.id, token=token)

    response = await client.post("/api/auth/verify-email", json={"token": token})
    assert response.status_code == 204
