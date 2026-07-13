import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.tender import Tender
from app.models.enums import ProcurementLaw
from app.schemas.tender import TenderOut

router = APIRouter()

@router.get("/filter", response_model=list[TenderOut])
async def filter_tenders(
    keywords: str | None = Query(default=None),
    region: str | None = Query(default=None),
    law: str | None = Query(default=None),
    price_from: str | None = Query(default=None),
    price_to: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Tender).options(selectinload(Tender.customer))
    if keywords and keywords.strip():
        for kw in keywords.split(","):
            kw = kw.strip()
            if kw:
                query = query.where(Tender.title.ilike(f"%{kw}%"))
    if region and region.strip() and region != "се регионы":
        query = query.where(Tender.region == region)
    if law and law.strip():
        laws = [l.strip() for l in law.split(",")]
        law_enums = []
        for l in laws:
            if l == "44-Ф": law_enums.append(ProcurementLaw.FZ_44)
            elif l == "223-Ф": law_enums.append(ProcurementLaw.FZ_223)
        if law_enums:
            query = query.where(Tender.law.in_(law_enums))
    if price_from and price_from.strip():
        try:
            query = query.where(Tender.initial_price >= float(price_from))
        except ValueError:
            pass
    if price_to and price_to.strip():
        try:
            query = query.where(Tender.initial_price <= float(price_to))
        except ValueError:
            pass
    query = query.order_by(Tender.published_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())

@router.get("/{tender_id}", response_model=TenderOut)
async def get_tender(tender_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Tender:
    result = await db.execute(select(Tender).options(selectinload(Tender.customer)).where(Tender.id == tender_id))
    tender = result.scalar_one_or_none()
    if tender is None:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

@router.get("", response_model=list[TenderOut])
async def list_tenders(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)) -> list[Tender]:
    result = await db.execute(select(Tender).options(selectinload(Tender.customer)).order_by(Tender.published_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())