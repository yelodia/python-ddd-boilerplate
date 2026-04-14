from arq import cron
from arq.connections import RedisSettings

from config import settings
from infra.worker.tasks.stock_replenishment import stock_replenishment_task
from infra.worker.tasks.stock_report import stock_report_task


class WorkerSettings:
    """
    Конфигурация arq-воркера.

    Запуск:
        arq src.infra.worker.settings.WorkerSettings

    Таски, перечисленные в `functions`, доступны для ручного постановки в очередь через arq-клиент.
    Таски в `cron_jobs` воркер запускает сам по расписанию — вручную их ставить в очередь не нужно.
    """

    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))

    functions = [
        stock_report_task,
        stock_replenishment_task,
    ]

    cron_jobs = [
        cron(stock_report_task, hour=6, minute=0),  # каждый день в 06:00
        cron(stock_replenishment_task, hour=6, minute=5),  # каждый день в 06:05, сразу после отчёта
    ]
