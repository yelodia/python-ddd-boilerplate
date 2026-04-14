"""
Точка запуска arq-воркера.

Используй этот скрипт вместо `arq src.infra.worker.settings.WorkerSettings`,
потому что arq 0.27.0 вызывает asyncio.get_event_loop() в синхронном контексте
прямо в Worker.__init__, а Python 3.12+ больше не создаёт loop неявно.

Запуск:
    python src/infra/worker/run.py
"""
import asyncio

import structlog

# Создаём loop до того, как arq создаст Worker — иначе RuntimeError на Python 3.12+
asyncio.set_event_loop(asyncio.new_event_loop())

from arq.worker import run_worker
from infra.worker.settings import WorkerSettings

logger = structlog.get_logger(__name__)

logger.info("arq worker starting", worker=WorkerSettings.__name__)
run_worker(WorkerSettings)
logger.info("arq worker stopped")
