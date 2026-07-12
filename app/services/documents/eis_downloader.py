from app.services.documents.base import BaseDocumentDownloader, DownloadResult
from app.services.parsers.eis.client import EISClient, EISClientError
import logging

logger = logging.getLogger(__name__)


class EISDocumentDownloader(BaseDocumentDownloader):

    @property
    def source_name(self) -> str:
        return "eis_44fz"

    async def download(self, document_url: str) -> DownloadResult:
        result = DownloadResult(
            tender_id="",
            document_url=document_url,
        )
        try:
            client = EISClient()
            content = client.download_archive_raw(document_url)
            result.file_content = content
            result.file_name = document_url.split("/")[-1] or "archive.zip"
            result.file_format = "zip"
            result.success = True
        except EISClientError as e:
            result.error = str(e)
            logger.warning("Ошибка загрузки документа %s: %s", document_url, e)
        return result
