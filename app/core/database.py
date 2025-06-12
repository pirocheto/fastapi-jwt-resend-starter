from collections.abc import AsyncGenerator
from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select

# from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.models import User
from app.schemas.user import UserCreate
from app.services import user_service

logger = getLogger(__name__)

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    future=True,
)


async def init_superuser(*, async_session: AsyncSession, email: str, username: str, password: str) -> None:
    statement = select(User).where(User.email == email)
    result = await async_session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=settings.DEFAULT_SUPERUSER_EMAIL,
            username=settings.DEFAULT_SUPERUSER_USERNAME,
            password=settings.DEFAULT_SUPERUSER_PASSWORD,
            is_superuser=True,
            email_verified=True,
        )
        user = await user_service.create_user(async_session=async_session, user_create=user_in)
        logger.info(f"Created superuser {user.email}")
    else:
        logger.info(f"Superuser {user.email} already exists")


async def init_db(async_session: AsyncSession) -> None:
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as async_session:
        yield async_session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]
