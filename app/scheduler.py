import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler = AsyncIOScheduler()


def clear_expired_tokens() -> None:
    logger.info(f"[{datetime.now()}] Deleting expired tokens")


def start() -> None:
    scheduler.add_job(
        clear_expired_tokens,
        trigger=CronTrigger(hour=3, minute=0),
        id="clear_expired_tokens",
        replace_existing=True,
    )
    logger.info("Scheduler started, job to clear expired tokens added.")
    scheduler.start()
