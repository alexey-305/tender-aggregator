from celery import Celery
from celery.schedules import crontab
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "tenderos",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    beat_schedule={
        # Сбор закупок — каждый час в рабочее время (8:00-20:00 МСК)
        "collect-every-hour": {
            "task": "collect_all_sources",
            "schedule": crontab(minute=0, hour="8-20"),
         },
        # Синхронизация с OpenSearch — каждые 15 минут
        "sync-search-every-15min": {
            "task": "sync_tenders_to_search",
            "schedule": crontab(minute="*/15"),
        },
    },
    task_routes={
        "collect_all_sources": {"queue": "default"},
        "sync_tenders_to_search": {"queue": "default"},
        "analyze_document": {"queue": "ai"},
    },
)
