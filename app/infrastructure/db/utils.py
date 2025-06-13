import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    from app.infrastructure.db.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


class HasSession(Protocol):
    session: AsyncSession


P = ParamSpec("P")
R = TypeVar("R")
S = TypeVar("S", bound=HasSession)


def transactional(method: Callable[..., Awaitable[R]]) -> Callable[..., Awaitable[R]]:
    """Decorator to wrap methods in a transaction.
    This ensures that the method runs within a database transaction context.
    If the method raises an exception, the transaction will be rolled back.
    If it completes successfully, the transaction will be committed."""

    @wraps(method)
    async def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:  # type: ignore
        async with self.session.begin():
            return await method(self, *args, **kwargs)

    return wrapper
