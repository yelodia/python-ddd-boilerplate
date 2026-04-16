"""
Точка запуска arq-воркера для тасков, запускаемых по расписанию.

Используй этот скрипт вместо `arq infra.worker.settings.CronJobsSettings`,
потому что arq 0.27.0 вызывает asyncio.get_event_loop() в синхронном контексте
прямо в Worker.__init__, а Python 3.12+ больше не создаёт loop неявно.

Запуск:
    python src/cron_tasks_worker.py
"""
import asyncio

import structlog

# Создаём loop до того, как arq создаст Worker — иначе RuntimeError на Python 3.12+
asyncio.set_event_loop(asyncio.new_event_loop())

from arq.worker import run_worker
from infra.worker.settings import CronJobsSettings

logger = structlog.get_logger(__name__)

logger.info("arq worker starting", worker=CronJobsSettings.__name__)
run_worker(CronJobsSettings)
logger.info("arq worker stopped")
