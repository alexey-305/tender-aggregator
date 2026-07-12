"""
Шаблон для нового источника закупок.
Скопируй этот файл, переименуй (например sberbank_collector.py) и реализуй три метода.
"""

from datetime import datetime, timezone

from app.services.collectors.base import BaseCollector, CollectionConfig, CollectionResult


class TemplateCollector(BaseCollector):

    @property
    def source_name(self) -> str:
        return "template_source"

    async def collect(self, config: CollectionConfig | None = None) -> CollectionResult:
        started_at = datetime.now(timezone.utc)

        # 1. Получить список закупок из источника (API или парсинг)
        # raw_items = await self._fetch_from_api(config)

        # 2. Для каждой закупки — нормализовать и сохранить
        # for item in raw_items:
        #     await self._save_tender(item)

        saved = 0
        errors = 0

        finished_at = datetime.now(timezone.utc)

        return CollectionResult(
            source=self.source_name,
            started_at=started_at,
            finished_at=finished_at,
            requested=0,
            downloaded=0,
            parsed=0,
            saved=saved,
            errors=errors,
        )

    async def health_check(self) -> bool:
        # Проверить, что источник отвечает
        return True
