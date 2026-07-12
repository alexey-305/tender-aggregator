import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import TenderDocument

router = APIRouter()


@router.get("/tenders/{tender_id}/documents")
async def get_tender_documents(
    tender_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TenderDocument).where(TenderDocument.tender_id == tender_id)
    )
    docs = result.scalars().all()
    return [
        {
            "id": str(doc.id),
            "title": doc.title,
            "file_type": doc.file_type,
            "source_url": doc.source_url,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }
        for doc in docs
    ]
