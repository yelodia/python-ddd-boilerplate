from arq import cron
from arq.connections import RedisSettings, create_pool

from config import settings
from infra.worker.tasks.event_dispatcher import dispatch_event
from infra.worker.tasks.stock_replenishment import stock_replenishment_task
from infra.worker.tasks.stock_report import stock_report_task


class WorkerSettings:
    """
    Конфигурация arq-воркера.

    Запуск:
        arq src.infra.worker.settings.WorkerSettings

    Таски, перечисленные в `functions`, доступны для ручной постановки в очередь через arq-клиент.
    Таски в `cron_jobs` воркер запускает сам по расписанию — вручную их ставить в очередь не нужно.
    """

    redis_settings = RedisSettings.from_dsn(str(settings.redis_url))

    @staticmethod
    async def on_startup(ctx: dict) -> None:
        """Создаёт Redis-соединение один раз при старте воркера и кладёт его в ctx для всех тасков."""
        ctx['redis'] = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))

    @staticmethod
    async def on_shutdown(ctx: dict) -> None:
        """Закрывает Redis-соединение при остановке воркера."""
        await ctx['redis'].aclose()

    functions = [  # type: ignore[assignment]
        dispatch_event,
        stock_report_task,
        stock_replenishment_task,
    ]

    cron_jobs = [
        cron(stock_report_task, hour=6, minute=0),  # каждый день в 06:00
        cron(stock_replenishment_task, hour=6, minute=5),  # каждый день в 06:05, сразу после отчёта
    ]
