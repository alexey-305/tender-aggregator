from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DownloadResult:
    tender_id: str
    document_url: str
    file_name: str | None = None
    file_content: bytes | None = None
    file_format: str | None = None
    success: bool = False
    error: str | None = None


class BaseDocumentDownloader(ABC):

    @property
    @abstractmethod
    def source_name(self) -> str:
        ...

    @abstractmethod
    async def download(self, document_url: str) -> DownloadResult:
        ...
