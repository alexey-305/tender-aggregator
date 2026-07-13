�їfrom functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://tender:tender@localhost:5432/tender_aggregator"

    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_index_tenders: str = "tenders"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    eis_ftp_host: str = "ftp.zakupki.gov.ru"

    eis_token: str | None = None
    eis_soap_url: str = "https://int44.zakupki.gov.ru/eis-integration/services/getDocsLE"
    eis_ws_namespace: str = "http://zakupki.gov.ru/fz44/get-docs-ip/ws"
    eis_local_proxy_url: str | None = None
    eis_curl_binary: str | None = None

    anthropic_api_key: str | None = None
    secret_key: str | None = None

    @property
    def opensearch_url(self) -> str:
        return f"http://{self.opensearch_host}:{self.opensearch_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
