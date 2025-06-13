# Base declarative, session maker, etc.
import logging
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
    async with AsyncSession(
        engine,
        # expire_on_commit=False,
    ) as session:
        yield session


logger = logging.getLogger(__name__)


async def init_db() -> None:
    from app.infrastructure.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
