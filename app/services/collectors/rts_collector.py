"""
Коллектор для РТС-тендер.
Использует открытый API для получения закупок.
"""

from datetime import datetime, timezone, date
import httpx
from app.services.collectors.base import BaseCollector, CollectionConfig, CollectionResult
from app.models.enums import ProcurementLaw, ProcurementMethod, TenderSource, TenderStatus
from app.db.session import async_session_maker
from app.models.tender import Tender
from sqlalchemy.dialects.postgresql import insert as pg_insert
import logging

logger = logging.getLogger(__name__)

RTS_API = "https://api.rts-tender.ru/api/v1/trades/search"


class RTSCollector(BaseCollector):

    @property
    def source_name(self) -> str:
        return "rts_tender"

    async def collect(self, config: CollectionConfig | None = None) -> CollectionResult:
        started_at = datetime.now(timezone.utc)
        config = config or CollectionConfig()
        saved = 0
        errors = 0

        try:
            async with httpx.AsyncClient(timeout=30, verify=False) as client:
                response = await client.post(
                    RTS_API,
                    json={
                        "page": 1,
                        "size": 100,
                        "sort": "publicationDate,desc",
                        "publishDateFrom": (config.date_from or date.today()).isoformat(),
                    },
                    headers={"Content-Type": "application/json"},
                )
                
                if response.status_code == 404:
                    # Try alternative API
                    response = await client.get(
                        "https://api.rts-tender.ru/api/v1/procedures",
                        params={"page": 1, "size": 100},
                        timeout=30,
                    )
                
                if response.status_code != 200:
                    logger.warning(f"RTS API returned {response.status_code}: {response.text[:200]}")
                    return CollectionResult(source=self.source_name, started_at=started_at, finished_at=datetime.now(timezone.utc), errors=1)

                data = response.json()
                tenders = data.get("content") or data.get("items") or data.get("data") or []

                async with async_session_maker() as session:
                    for item in tenders:
                        try:
                            external_id = str(item.get("id") or item.get("tradeId") or item.get("procedureId"))
                            title = item.get("name") or item.get("title") or item.get("tradeName") or "—"
                            price = item.get("initialPrice") or item.get("price")
                            customer_name = item.get("customer") or item.get("customerName") or {}
                            if isinstance(customer_name, dict):
                                customer_name = customer_name.get("name") or customer_name.get("fullName")
                            published_at = item.get("publicationDate") or item.get("publishDate")
                            deadline = item.get("endDate") or item.get("deadline") or item.get("applicationEndDate")

                            values = dict(
                                source=TenderSource.RTS_TENDER,
                                external_id=external_id,
                                law=ProcurementLaw.FZ_44,
                                title=title,
                                procurement_method=ProcurementMethod.ELECTRONIC_AUCTION,
                                status=TenderStatus.PUBLISHED,
                                initial_price=price,
                                region=config.region or "77",
                                published_at=published_at,
                                submission_deadline=deadline,
                                raw_data=item,
                            )

                            stmt = pg_insert(Tender).values(**values)
                            stmt = stmt.on_conflict_do_update(
                                constraint="uq_tender_source_external_id",
                                set_={k: v for k, v in values.items() if k not in ("source", "external_id")},
                            )
                            await session.execute(stmt)
                            saved += 1
                        except Exception as e:
                            logger.error(f"Failed to save RTS tender {item.get('id')}: {e}")
                            errors += 1

                    await session.commit()

        except Exception as e:
            logger.error(f"RTS collector error: {e}")
            errors = 1

        finished_at = datetime.now(timezone.utc)
        return CollectionResult(
            source=self.source_name,
            started_at=started_at,
            finished_at=finished_at,
            saved=saved,
            errors=errors,
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                r = await client.get("https://www.rts-tender.ru")
                return r.status_code == 200
        except Exception:
            return False