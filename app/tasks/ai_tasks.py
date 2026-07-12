from app.tasks.celery_app import celery_app
from app.services.ai.service import AIService
from app.models.document import TenderDocument
from app.db.session import async_session_maker
from sqlalchemy import select, update
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="analyze_document")
def analyze_document(document_id: str):
    """Анализирует один документ через AI и сохраняет извлечённые требования."""

    async def _run():
        ai = AIService()
        async with async_session_maker() as session:
            result = await session.execute(
                select(TenderDocument).where(TenderDocument.id == document_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                return {"ok": False, "error": "Document not found"}

            raw_text = getattr(doc, "raw_text", None)
            if not raw_text:
                return {"ok": False, "error": "Document has no extracted text"}

            analysis = await ai.analyze_document(raw_text)

            if analysis.error:
                logger.warning("AI analysis error for doc %s: %s", document_id, analysis.error)
                return {"ok": False, "error": analysis.error}

            if analysis.requirements:
                from app.models.document import DocumentRequirement
                for lic in analysis.requirements.licenses:
                    session.add(DocumentRequirement(
                        document_id=doc.id,
                        requirement_type="license",
                        description=lic,
                    ))
                for gost in analysis.requirements.gosts:
                    session.add(DocumentRequirement(
                        document_id=doc.id,
                        requirement_type="gost",
                        description=gost,
                    ))
                for risk in analysis.requirements.risks:
                    session.add(DocumentRequirement(
                        document_id=doc.id,
                        requirement_type="risk",
                        description=risk,
                    ))

            doc.status = "analyzed"
            await session.commit()

            return {
                "ok": True,
                "document_id": document_id,
                "model": analysis.model_used,
                "tokens": analysis.tokens_used,
            }

    return asyncio.run(_run())
