"""
Сервис загрузки документов. Находит закупки, у которых ещё нет скачанных файлов,
и скачивает их через соответствующий загрузчик источника.
"""

import logging
from app.models.tender import Tender
from app.models.document import TenderDocument
from app.services.documents.eis_downloader import EISDocumentDownloader
from app.db.session import async_session_maker
from sqlalchemy import select

logger = logging.getLogger(__name__)


class DocumentDownloadService:

    async def download_for_tender(self, tender_id: str) -> int:
        """Скачивает все документы для конкретной закупки. Возвращает количество скачанных."""
        async with async_session_maker() as session:
            result = await session.execute(
                select(Tender).where(Tender.id == tender_id)
            )
            tender = result.scalar_one_or_none()
            if not tender:
                return 0

            raw_data = tender.raw_data or {}
            doc_urls = self._extract_doc_urls(raw_data)

            downloader = self._get_downloader(tender.source.value)
            if not downloader:
                return 0

            downloaded = 0
            for url in doc_urls:
                doc_result = await downloader.download(url)
                if doc_result.success:
                    doc = TenderDocument(
                        tender_id=tender.id,
                        file_url=url,
                        file_name=doc_result.file_name,
                        file_format=doc_result.file_format,
                        file_content=doc_result.file_content,
                        status="downloaded",
                    )
                    session.add(doc)
                    downloaded += 1

            await session.commit()
            return downloaded

    def _extract_doc_urls(self, raw_data: dict) -> list[str]:
        """Извлекает URL-ы документов из raw_data закупки."""
        urls = []
        for key, value in raw_data.items():
            if isinstance(value, str) and value.startswith("http"):
                urls.append(value)
            elif isinstance(value, dict):
                urls.extend(self._extract_doc_urls(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        urls.extend(self._extract_doc_urls(item))
                    elif isinstance(item, str) and item.startswith("http"):
                        urls.append(item)
        return urls

    def _get_downloader(self, source: str):
        if source == "eis_44fz":
            return EISDocumentDownloader()
        return None
