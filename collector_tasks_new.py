from app.tasks.celery_app import celery_app
from app.services.collectors.orchestrator import get_orchestrator
from app.services.collectors.base import CollectionConfig
from app.models.search_key import SearchKey
from app.db.session import async_session_maker
from sqlalchemy import select
import asyncio
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="collect_all_sources")
def collect_all_sources():
    """Собирает закупки для всех регионов из активных шаблонов + Москва по умолчанию."""
    
    async def _run():
        regions = set(["77"])  # Москва всегда
        
        # Получаем все уникальные регионы из шаблонов
        async with async_session_maker() as session:
            result = await session.execute(select(SearchKey.region))
            for row in result.scalars().all():
                if row:
                    for r in row.split(","):
                        r = r.strip()
                        if r and r.isdigit():
                            regions.add(r)
        
        logger.info(f"Сбор для регионов: {regions}")
        
        total_saved = 0
        total_errors = 0
        
        for region in regions:
            config = CollectionConfig(region=region)
            orchestrator = get_orchestrator()
            results = await orchestrator.run_all(config)
            
            for r in results:
                logger.info(f"Регион {region}: {r.source} — saved={r.saved} errors={r.errors}")
                total_saved += r.saved
                total_errors += r.errors
        
        return {
            "ok": total_errors == 0,
            "total_saved": total_saved,
            "total_errors": total_errors,
        }
    
    return asyncio.run(_run())