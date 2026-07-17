"""
Orchestrator — запускает все активные Collector'ы по расписанию.
Пока синхронно, позже каждый коллектор пойдёт в отдельную Celery-задачу.
"""

import logging
from datetime import datetime, timezone

from app.services.collectors.base import BaseCollector, CollectionConfig, CollectionResult

logger = logging.getLogger(__name__)


class CollectorOrchestrator:

    def __init__(self, collectors: list[BaseCollector] | None = None):
        self.collectors = collectors or []

    def register(self, collector: BaseCollector) -> None:
        self.collectors.append(collector)

    async def run_all(self, config: CollectionConfig | None = None) -> list[CollectionResult]:
        results: list[CollectionResult] = []
        for collector in self.collectors:
            logger.info("Запуск коллектора: %s", collector.source_name)
            try:
                result = await collector.collect(config)
                logger.info("Коллектор %s завершён: saved=%d errors=%d", collector.source_name, result.saved, result.errors)
            except Exception:
                logger.exception("Коллектор %s упал с ошибкой", collector.source_name)
                result = CollectionResult(
                    source=collector.source_name,
                    started_at=datetime.now(timezone.utc),
                    finished_at=datetime.now(timezone.utc),
                    errors=1,
                )
            results.append(result)
        return results


_orchestrator: CollectorOrchestrator | None = None


def get_orchestrator() -> CollectorOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        from app.services.collectors import EISCollector
        _orchestrator = CollectorOrchestrator()
        _orchestrator.register(EISCollector())
    return _orchestrator


