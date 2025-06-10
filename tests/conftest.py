from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.database import engine, init_db
from app.main import app
from app.models import User
from tests.utils.user import create_random_user, user_authentication_headers

fake = Faker("fr_FR")


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def normal_user_token_headers(db: Session) -> dict[str, str]:
    user = create_random_user(db=db)
    return user_authentication_headers(db_user=user)


@pytest.fixture(scope="function")
def mocked_send_email() -> Generator[MagicMock]:
    with patch("resend.Emails.send") as mock:
        mock.return_value = {"id": fake.uuid4()}
        yield mock
