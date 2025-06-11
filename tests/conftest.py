from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import engine
from app.main import app
from app.models import Base
from tests.factories import UserFactory


@pytest.fixture(scope="session", autouse=True)
def session() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def user_factory(session: Session) -> UserFactory:
    return UserFactory(session)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client
