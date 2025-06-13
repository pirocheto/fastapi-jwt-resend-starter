# Base declarative, session maker, etc.
from collections.abc import AsyncGenerator
from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings

logger = getLogger(__name__)

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    future=True,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session
