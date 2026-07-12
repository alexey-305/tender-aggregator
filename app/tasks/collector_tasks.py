from app.tasks.celery_app import celery_app
from app.services.collectors.orchestrator import get_orchestrator
from app.services.collectors.base import CollectionConfig
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="collect_all_sources")
def collect_all_sources(region: str = "77"):
    """Запускает все коллекторы. Вызывается по расписанию из Celery Beat."""
    config = CollectionConfig(region=region)
    orchestrator = get_orchestrator()

    async def _run():
        return await orchestrator.run_all(config)

    results = asyncio.run(_run())

    for r in results:
        logger.info(
            "Celery task: %s — saved=%d errors=%d",
            r.source, r.saved, r.errors,
        )

    return {
        "ok": all(r.ok for r in results),
        "total_saved": sum(r.saved for r in results),
        "total_errors": sum(r.errors for r in results),
    }
