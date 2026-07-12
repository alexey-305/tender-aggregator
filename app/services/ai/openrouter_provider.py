import json
import logging
import httpx
from app.core.config import get_settings
from app.services.ai.base import BaseAIProvider, AIAnalysisResult, ExtractedRequirements

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_INSTRUCTION = """Ты — эксперт по государственным закупкам РФ (44-ФЗ, 223-ФЗ).
Проанализируй текст закупочной документации и извлеки структурированные требования в JSON:

{
  "goods": [{"name": "...", "quantity": ..., "unit": "...", "characteristics": {...}}],
  "licenses": ["лицензия МЧС", ...],
  "gosts": ["ГОСТ Р 12345-2020", ...],
  "deadlines": {"submission": "YYYY-MM-DD", "contract": "YYYY-MM-DD"},
  "financial_requirements": {"security_amount": "...", "advance": "..."},
  "forms": ["форма 1", "форма 2"],
  "risks": ["высокий аванс без обеспечения", ...]
}

Если какого-то поля нет — оставь пустой список или null.
Отвечай только JSON, без пояснений."""


class OpenRouterProvider(BaseAIProvider):

    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def analyze_document(self, text: str, instruction: str | None = None) -> AIAnalysisResult:
        instruction = instruction or DEFAULT_INSTRUCTION
        api_key = settings.anthropic_api_key
        if not api_key:
            return AIAnalysisResult(document_id="", error="API key not set", model_used=self.provider_name)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "anthropic/claude-sonnet-4.5",
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": text[:30000]},
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
            if response.status_code != 200:
                return AIAnalysisResult(document_id="", error=f"HTTP {response.status_code}: {response.text[:500]}", model_used=self.provider_name)

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)

            try:
                json_match = content
                if "`json" in content:
                    json_match = content.split("`json")[1].split("`")[0]
                elif "`" in content:
                    json_match = content.split("`")[1].split("`")[0]
                parsed = json.loads(json_match.strip())
                requirements = ExtractedRequirements(
                    goods=parsed.get("goods", []),
                    licenses=parsed.get("licenses", []),
                    gosts=parsed.get("gosts", []),
                    deadlines=parsed.get("deadlines", {}),
                    financial_requirements=parsed.get("financial_requirements", {}),
                    forms=parsed.get("forms", []),
                    risks=parsed.get("risks", []),
                    raw_response=content,
                )
                return AIAnalysisResult(
                    document_id="",
                    requirements=requirements,
                    summary=content[:500],
                    model_used=self.provider_name,
                    tokens_used=tokens,
                )
            except json.JSONDecodeError:
                return AIAnalysisResult(
                    document_id="",
                    summary=content[:1000],
                    error="JSON parse error",
                    model_used=self.provider_name,
                    tokens_used=tokens,
                )
        except Exception as e:
            logger.exception("OpenRouter error")
            return AIAnalysisResult(document_id="", error=str(e), model_used=self.provider_name)

    async def health_check(self) -> bool:
        api_key = settings.anthropic_api_key
        return bool(api_key)
