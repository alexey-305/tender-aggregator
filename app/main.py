from fastapi import FastAPI

from app.api.v1.tenders import router as tenders_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Tender Aggregator API",
    version="0.1.0",
    description="Агрегатор торгов: поиск закупок + (в разработке) ИИ-ассистент по подготовке заявок",
)

app.include_router(tenders_router, prefix="/api/v1/tenders", tags=["tenders"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "env": settings.app_env}
