from app.services.ai.base import BaseAIProvider, AIAnalysisResult
from app.services.ai.openrouter_provider import OpenRouterProvider
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Фасад для AI. Система работает только через этот класс, не зная деталей провайдера."""

    def __init__(self, provider: BaseAIProvider | None = None):
        self._provider = provider or OpenRouterProvider()

    @property
    def provider_name(self) -> str:
        return self._provider.provider_name

    async def analyze_document(self, text: str, instruction: str | None = None) -> AIAnalysisResult:
        return await self._provider.analyze_document(text, instruction)

    async def health_check(self) -> bool:
        return await self._provider.health_check()
