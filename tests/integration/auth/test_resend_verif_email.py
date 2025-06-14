import pytest
from httpx import AsyncClient

from tests.factories import UserFactory, VerificationTokenFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_resend_verif_email_success(
    client: AsyncClient,
    user_factory: UserFactory,
    verif_token_factory: VerificationTokenFactory,
) -> None:
    token = fake.uuid4()

    user = await user_factory.create(is_verified=False)
    await verif_token_factory.create(user.id, token=token)

    response = await client.post("api/auth/resend-verification", json={"email": user.email})
    assert response.status_code == 204
