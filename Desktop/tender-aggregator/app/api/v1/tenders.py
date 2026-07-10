import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.tender import Tender
from app.schemas.tender import TenderOut

router = APIRouter()


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
    """
    Базовый листинг напрямую из Postgres, отсортированный по дате публикации.
    Это временная реализация для проверки, что пайплайн end-to-end работает.
    Полнотекстовый поиск и фасетная фильтрация переедут на OpenSearch
    следующим шагом (services/search).
    """
    result = await db.execute(
        select(Tender)
        .options(selectinload(Tender.customer))
        .order_by(Tender.published_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
