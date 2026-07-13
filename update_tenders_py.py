from app.api.v1.tenders import router
from fastapi import Query, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.tender import Tender
from app.schemas.tender import TenderOut
from app.models.enums import ProcurementLaw, ProcurementMethod

@router.get("/filter", response_model=list[TenderOut])
async def filter_tenders(
    keywords: str | None = Query(default=None),
    exclude_keywords: str | None = Query(default=None),
    region: str | None = Query(default=None),
    law: str | None = Query(default=None),
    method: str | None = Query(default=None),
    price_from: float | None = Query(default=None),
    price_to: float | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(Tender).options(selectinload(Tender.customer))
    
    if keywords:
        for kw in keywords.split(","):
            kw = kw.strip()
            if kw:
                query = query.where(Tender.title.ilike(f"%{kw}%"))
    
    if exclude_keywords:
        for kw in exclude_keywords.split(","):
            kw = kw.strip()
            if kw:
                query = query.where(~Tender.title.ilike(f"%{kw}%"))
    
    if region and region != "се регионы":
        query = query.where(Tender.region == region)
    
    if law:
        laws = [l.strip() for l in law.split(",")]
        law_enums = []
        for l in laws:
            if l == "44-Ф": law_enums.append(ProcurementLaw.FZ_44)
            elif l == "223-Ф": law_enums.append(ProcurementLaw.FZ_223)
            elif l == "615 ": law_enums.append(ProcurementLaw.PP_615)
            elif l == "оммерческие": law_enums.append(ProcurementLaw.COMMERCIAL)
        if law_enums:
            query = query.where(Tender.law.in_(law_enums))
    
    if method and method != "all":
        try:
            method_enum = ProcurementMethod(method)
            query = query.where(Tender.procurement_method == method_enum)
        except ValueError:
            pass
    
    if price_from is not None:
        query = query.where(Tender.initial_price >= price_from)
    if price_to is not None:
        query = query.where(Tender.initial_price <= price_to)
    
    query = query.order_by(Tender.published_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())