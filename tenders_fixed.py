import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.tender import Tender
from app.schemas.tender import TenderOut
from app.services.search.service import SearchService

router = APIRouter()
_search: SearchService | None = None


def _get_search() -> SearchService:
    global _search
    if _search is None:
        _search = SearchService()
        _search.ensure_index()
    return _search


@router.get("/search", response_model=dict)
def search_tenders(
    q: str = Query(default="", description="Поисковый запрос"),
    law: str | None = Query(default=None),
    method: str | None = Query(default=None),
    region: str | None = Query(default=None),
    status: str | None = Query(default=None),
    price_from: float | None = Query(default=None),
    price_to: float | None = Query(default=None),
    okpd2: str | None = Query(default=None),
    size: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    filters = {}
    if law:
        filters["law"] = law
    if method:
        filters["procurement_method"] = method
    if region:
        filters["region"] = region
    if status:
        filters["status"] = status
    if okpd2:
        filters["okpd2_codes"] = okpd2

    search = _get_search()
    result = search.search(query=q, filters=filters if filters else None, size=size, offset=offset)
    hits = result["hits"]["hits"]
    return {
        "total": result["hits"]["total"]["value"],
        "size": size,
        "offset": offset,
        "results": [
            {
                "id": hit["_id"],
                **hit["_source"],
            }
            for hit in hits
        ],
    }


@router.get("/{tender_id}", response_model=TenderOut)
async def get_tender(tender_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Tender:
    result = await db.execute(
        select(Tender).options(selectinload(Tender.customer)).where(Tender.id == tender_id)
    )
    tender = result.scalar_one_or_none()
    if tender is None:
        raise HTTPException(status_code=404, detail="Закупка не найдена")
    return tender


@router.get("", response_model=list[TenderOut])
async def list_tenders(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[Tender]:
    result = await db.execute(
        select(Tender)
        .options(selectinload(Tender.customer))
        .order_by(Tender.published_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())

