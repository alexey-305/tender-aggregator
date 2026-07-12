"""
Ручной запуск оркестратора: python -m app.services.collectors.run --region 77
"""

import argparse
import asyncio
import logging
from datetime import date, datetime

from app.services.collectors.base import CollectionConfig
from app.services.collectors.orchestrator import get_orchestrator


def _cli() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Запуск сборщиков закупок")
    parser.add_argument("--region", default="77", help="Код региона (по умолчанию 77 — Москва)")
    parser.add_argument("--date", default=None, help="Дата в формате YYYY-MM-DD (по умолчанию сегодня)")
    args = parser.parse_args()

    exact_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()

    config = CollectionConfig(region=args.region, date_from=exact_date)
    orchestrator = get_orchestrator()

    logger.info("Запуск оркестратора: регион=%s дата=%s", config.region, config.date_from)
    results = asyncio.run(orchestrator.run_all(config))

    for r in results:
        logger.info(
            "Результат %s: запрошено=%d скачано=%d разобрано=%d сохранено=%d ошибок=%d за %.1fс",
            r.source,
            r.requested,
            r.downloaded,
            r.parsed,
            r.saved,
            r.errors,
            (r.finished_at - r.started_at).total_seconds(),
        )


if __name__ == "__main__":
    _cli()
