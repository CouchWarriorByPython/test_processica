import logging
from typing import Any

from arq.connections import RedisSettings

from src.config import get_settings
from src.workers.tasks import validate_address_task

logger = logging.getLogger(__name__)
settings = get_settings()


async def startup(_ctx: dict[str, Any]) -> None:
    logger.info("ARQ worker starting...")


async def shutdown(_ctx: dict[str, Any]) -> None:
    logger.info("ARQ worker shutting down...")


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [validate_address_task]
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    job_timeout = 300
    keep_result = 3600
    retry_jobs = True
    max_tries = 3
