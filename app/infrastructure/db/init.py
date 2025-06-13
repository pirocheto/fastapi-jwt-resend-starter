import logging

from app.infrastructure.db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    from app.infrastructure.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
