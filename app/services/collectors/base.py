from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class CollectionResult:
    source: str
    started_at: datetime
    finished_at: datetime
    requested: int = 0
    downloaded: int = 0
    parsed: int = 0
    saved: int = 0
    errors: int = 0

    @property
    def ok(self) -> bool:
        return self.errors == 0


@dataclass
class CollectionConfig:
    region: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    extra: dict | None = None


class BaseCollector(ABC):

    @property
    @abstractmethod
    def source_name(self) -> str:
        ...

    @abstractmethod
    async def collect(self, config: CollectionConfig | None = None) -> CollectionResult:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
