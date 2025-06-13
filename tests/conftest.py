from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Base
from app.infrastructure.db.session import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def create_test_database() -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as async_session:
        yield async_session
        # await async_session.rollback()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
