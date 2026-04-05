"""Arq worker composition root (analogous to main.py for FastAPI)."""

from arq.connections import RedisSettings

from src.application.items.tasks import process_item_export
from src.config import get_settings

settings = get_settings()

_redis = str(settings.redis_url)
_host, _port = _redis.split("//")[1].rsplit(":", 1)
_port_int = int(_port.split("/")[0])
_db = int(_port.split("/")[1]) if "/" in _port else 0


class WorkerSettings:
    functions = [
        process_item_export,
    ]

    redis_settings = RedisSettings(host=_host, port=_port_int, database=_db)

    max_jobs = 10
    job_timeout = 300
    keep_result = 3600
    retry_jobs = True
    max_tries = 3
