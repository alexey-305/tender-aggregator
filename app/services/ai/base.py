from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ExtractedRequirements:
    goods: list[dict] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    gosts: list[str] = field(default_factory=list)
    deadlines: dict = field(default_factory=dict)
    financial_requirements: dict = field(default_factory=dict)
    forms: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    raw_response: str | None = None


@dataclass
class AIAnalysisResult:
    document_id: str
    requirements: ExtractedRequirements | None = None
    summary: str | None = None
    error: str | None = None
    model_used: str | None = None
    tokens_used: int = 0


class BaseAIProvider(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    async def analyze_document(self, text: str, instruction: str | None = None) -> AIAnalysisResult:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
