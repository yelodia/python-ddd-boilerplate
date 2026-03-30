import asyncio

import structlog

logger = structlog.get_logger(__name__)


async def process_item_export(ctx: dict, item_id: int) -> dict:
    structlog.contextvars.bind_contextvars(item_id=item_id, job="export")
    logger.info("export_started")
    # TODO: replace with real service call, e.g. await use_cases.export_item(item_id)
    await asyncio.sleep(0)
    logger.info("export_finished")
    structlog.contextvars.unbind_contextvars("item_id", "job")
    return {"status": "done", "item_id": item_id}
