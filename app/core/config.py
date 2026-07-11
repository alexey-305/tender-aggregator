from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://tender:tender@localhost:5432/tender_aggregator"

    opensearch_host: str = "localhost"
    opensearch_port: int = 9200
    opensearch_index_tenders: str = "tenders"

    eis_ftp_host: str = "ftp.zakupki.gov.ru"  # historical, больше не используется — оставлено для справки

    # SOAP-сервис отдачи информации ЕИС (пришёл на смену FTP с 01.01.2025).
    # С 04.10.2025 старый домен int44.zakupki.gov.ru отключён — актуальный адрес int.zakupki.gov.ru.
    # Сервис требует ГОСТ-TLS, обычный httpx/OpenSSL такое соединение установить не может —
    # нужен локальный туннель (например, CryptoPro Stunnel), см. eis_local_proxy_url.
    eis_token: str | None = None  # individualPerson_token или юрлицо-токен, из ЛК ЕИС
    eis_soap_url: str = "https://int.zakupki.gov.ru/eis-integration/services/getDocsIP"
    eis_ws_namespace: str = "http://zakupki.gov.ru/fz44/get-docs-ip/ws"

    # Если задано — все запросы к ЕИС идут через этот адрес (локальный ГОСТ-TLS туннень,
    # например http://127.0.0.1:8443) вместо eis_soap_url напрямую.
    eis_local_proxy_url: str | None = None

    # Путь к ГОСТ-TLS-совместимому curl из состава КриптоПро CSP (обычно
    # /opt/cprocsp/bin/curl на Linux/macOS). Если задан — запросы к ЕИС идут
    # через subprocess-вызов этого curl вместо httpx, потому что стандартный
    # httpx/OpenSSL ГОСТ-TLS не поддерживает, а этот curl — да.
    eis_curl_binary: str | None = None

    anthropic_api_key: str | None = None

    @property
    def opensearch_url(self) -> str:
        return f"http://{self.opensearch_host}:{self.opensearch_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
