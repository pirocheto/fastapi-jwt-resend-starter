import logging
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from sqlalchemy import delete

from app.core.database import get_db
from app.models import RefreshToken

scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def clear_expired_tokens() -> None:
    logger.info(f"[{datetime.now()}] Deleting expired tokens")

    session = next(get_db())
    statement = delete(RefreshToken).where(RefreshToken.expires_at < datetime.now())
    session.execute(statement)
    session.commit()

    # Supprime tous les email verification tokens
    # session.query(EmailVerificationToken).delete(synchronize_session=False)

    # # Supprime tous les password reset tokens
    # session.query(PasswordResetToken).delete(synchronize_session=False)

    session.commit()


scheduler.add_job(
    clear_expired_tokens,
    # trigger=CronTrigger(hour=4, minute=0, day="*/2"),
    trigger=CronTrigger(second="*/2"),
    id="clear_expired_tokens",
    replace_existing=True,
)


@contextmanager
def scheduler_context() -> Generator[None]:
    """Context manager to start and stop the scheduler with the FastAPI app lifecycle."""
    try:
        scheduler.start()
        logger.info("Scheduler started")
        yield
    finally:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
        print("Scheduler stopped")
