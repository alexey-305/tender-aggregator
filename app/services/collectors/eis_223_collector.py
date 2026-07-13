from datetime import date, datetime, timezone
from app.services.collectors.base import BaseCollector, CollectionConfig, CollectionResult

class EIS223Collector(BaseCollector):

    @property
    def source_name(self) -> str:
        return "eis_223fz"

    async def collect(self, config: CollectionConfig | None = None) -> CollectionResult:
        config = config or CollectionConfig()
        region = config.region or "77"
        exact_date = config.date_from or date.today()
        started_at = datetime.now(timezone.utc)

        from app.services.parsers.eis.sync import sync_region_date
        from app.services.parsers.eis.document_types_223 import DEFAULT_DOCUMENT_TYPES_223, NOTIFICATION_SUBSYSTEM_TYPE_223

        stats = await sync_region_date(
            region=region,
            exact_date=exact_date,
            document_types=DEFAULT_DOCUMENT_TYPES_223,
            subsystem_type=NOTIFICATION_SUBSYSTEM_TYPE_223,
            law_type="223",
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
        return True