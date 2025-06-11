import logging
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.models import EmailVerificationToken, PasswordResetToken, RefreshToken

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def purge_expired_tokens(session: Session) -> None:
    """Remove expired or invalid tokens from the database."""

    now = datetime.now()

    cleanup_map = {
        RefreshToken: (RefreshToken.expires_at < now) | (RefreshToken.is_revoked),
        PasswordResetToken: (PasswordResetToken.expires_at < now) | (PasswordResetToken.used),
        EmailVerificationToken: (EmailVerificationToken.expires_at < now) | (EmailVerificationToken.used),
    }

    for model, condition in cleanup_map.items():
        session.execute(delete(model).where(condition))

    session.commit()


def token_cleanup_job() -> None:
    with Session(engine) as session:
        logger.info("Purging expired tokens from the database")
        purge_expired_tokens(session)
        logger.info("Expired tokens purged successfully")


scheduler.add_job(
    token_cleanup_job,
    # trigger=CronTrigger(hour=4, minute=0, day="*/2"),
    trigger=CronTrigger(second="*/2"),
    id="clear_expired_tokens",
    replace_existing=True,
)


@contextmanager
def real_scheduler_context() -> Generator[None]:
    """Context manager to start and stop the scheduler with the FastAPI app lifecycle."""
    try:
        scheduler.start()
        logger.info("Scheduler started")
        yield
    finally:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
        print("Scheduler stopped")


@contextmanager
def nnop_scheduler_context() -> Generator[None]:
    """No-op context manager for environments without a real scheduler."""
    yield


scheduler_context = real_scheduler_context if settings.ENVIRONMENT != "local" else nnop_scheduler_context
