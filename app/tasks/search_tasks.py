from app.tasks.celery_app import celery_app
from app.services.search.service import SearchService
from app.models.tender import Tender
from app.db.session import async_session_maker
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="sync_tenders_to_search")
def sync_tenders_to_search():
    async def _run():
        search = SearchService()
        search.ensure_index()

        async with async_session_maker() as session:
            result = await session.execute(
                select(Tender)
                .options(selectinload(Tender.customer))
                .where(Tender.indexed_at.is_(None))
                .limit(500)
            )
            tenders = result.scalars().all()

            if not tenders:
                search.close()
                return {"ok": True, "synced": 0}

            docs = []
            now = datetime.now(timezone.utc)
            for tender in tenders:
                docs.append({
                    "id": str(tender.id),
                    "external_id": tender.external_id,
                    "source": tender.source.value if tender.source else None,
                    "law": tender.law.value if tender.law else None,
                    "title": tender.title,
                    "description": tender.description,
                    "status": tender.status.value if tender.status else None,
                    "procurement_method": tender.procurement_method.value if tender.procurement_method else None,
                    "region": tender.region,
                    "initial_price": float(tender.initial_price) if tender.initial_price else None,
                    "customer_name": tender.customer.name if tender.customer else None,
                    "customer_inn": tender.customer.inn if tender.customer else None,
                    "okpd2_codes": tender.okpd2_codes,
                    "published_at": tender.published_at.isoformat() if tender.published_at else None,
                    "submission_deadline": tender.submission_deadline.isoformat() if tender.submission_deadline else None,
                })
                tender.indexed_at = now

            search.index_tenders_bulk(docs)
            await session.commit()
            search.close()

            return {"ok": True, "synced": len(docs)}

    return asyncio.run(_run())
