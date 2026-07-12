"""
EIS Collector — обёртка над sync_region_date для единого интерфейса BaseCollector.
"""

from datetime import date, datetime, timezone

from app.services.collectors.base import BaseCollector, CollectionConfig, CollectionResult
from app.services.parsers.eis.sync import sync_region_date


class EISCollector(BaseCollector):

    @property
    def source_name(self) -> str:
        return "eis_44fz"

    async def collect(self, config: CollectionConfig | None = None) -> CollectionResult:
        config = config or CollectionConfig()
        region = config.region or "77"
        exact_date = config.date_from or date.today()

        started_at = datetime.now(timezone.utc)

        stats = await sync_region_date(
            region=region,
            exact_date=exact_date,
        )

        finished_at = datetime.now(timezone.utc)

        return CollectionResult(
            source=self.source_name,
            started_at=started_at,
            finished_at=finished_at,
            requested=stats.get("requested", 0),
            downloaded=stats.get("downloaded", 0),
            parsed=stats.get("parsed", 0),
            saved=stats.get("saved", 0),
            errors=stats.get("errors", 0),
        )

    async def health_check(self) -> bool:
        try:
            from app.services.parsers.eis.client import EISClient
            client = EISClient()
            return client.token is not None
        except Exception:
            return False
