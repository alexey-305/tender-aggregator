"""
Клиент SOAP-сервиса отдачи информации ЕИС (getDocsIP).

Пришёл на смену FTP-серверу zakupki.gov.ru, закрытому с 01.01.2025.
Формат запроса подтверждён по нескольким независимым практическим
источникам (официальная инструкция ЕИС + опыт разработчиков в 2024-2025),
но НЕ протестирован против реального сервиса из этого окружения —
zakupki.gov.ru недоступен из песочницы, где писался этот код.
Первый реальный прогон нужно делать в вашем окружении с вашим токеном
и внимательно смотреть на текст ошибки, если она будет — сервис у ЕИС
исторически нестабилен и менял адреса/поведение несколько раз за 2025 год.
"""

import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import httpx
from lxml import etree
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings

settings = get_settings()

# Реальное значение SOAPAction взято из живого WSDL сервиса (проверено:
# GET .../getDocsIP?wsdl вернул 200 и это значение в wsdl:binding).
SOAP_ACTION = "http://zakupki.gov.ru/fz44/queue/ws/get-docs-ip"

SOAP_ENVELOPE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="{namespace}">
  <soapenv:Header>
    <individualPerson_token>{token}</individualPerson_token>
  </soapenv:Header>
  <soapenv:Body>
    <ws:getDocsByOrgRegionRequest>
      <index>
        <id>{request_id}</id>
        <createDateTime>{created_at}</createDateTime>
        <mode>PROD</mode>
      </index>
      <selectionParams>
        <orgRegion>{org_region}</orgRegion>
        <subsystemType>{subsystem_type}</subsystemType>
        <documentType44>{document_type}</documentType44>
        <periodInfo>
          <exactDate>{exact_date}</exactDate>
        </periodInfo>
      </selectionParams>
    </ws:getDocsByOrgRegionRequest>
  </soapenv:Body>
</soapenv:Envelope>"""

# Порядок дочерних тегов в selectionParams важен для ЕИС — сервер отклоняет
# запрос с "правильными" тегами в "неправильном" порядке (это подтверждено
# на практике несколькими независимо друг от друга разработчиками).


class EISClientError(Exception):
    """Ошибка при обращении к сервису отдачи информации ЕИС."""


class EISAuthError(EISClientError):
    """Токен не принят сервисом (просрочен/невалиден/не тот тип сервиса)."""


@dataclass
class ArchiveReference:
    """Ссылка на архив с документами, полученная в ответ на запрос."""

    url: str
    document_type: str
    region: str
    requested_date: date


class EISClient:
    def __init__(self, token: str | None = None, soap_url: str | None = None) -> None:
        self.token = token or settings.eis_token
        self.real_soap_url = soap_url or settings.eis_soap_url
        # Если задан локальный ГОСТ-TLS туннель — физически ходим туда напрямую (httpx).
        self.eis_local_proxy_url = settings.eis_local_proxy_url
        # Если задан ГОСТ-совместимый curl (например, из КриптоПро CSP:
        # /opt/cprocsp/bin/curl) — ходим через subprocess-вызов этого curl,
        # т.к. обычный httpx/OpenSSL ГОСТ-TLS не поддерживает.
        self.curl_binary = settings.eis_curl_binary
        if not self.token:
            raise EISAuthError(
                "Не задан EIS_TOKEN. Получить токен: личный кабинет ЕИС -> "
                "pmd.zakupki.gov.ru/pmd/lk/token (требуется действующая ЭЦП)."
            )

    def _build_request(self, org_region: str, subsystem_type: str, document_type: str, exact_date: date) -> str:
        return SOAP_ENVELOPE_TEMPLATE.format(
            namespace=settings.eis_ws_namespace,
            token=self.token,
            request_id=str(uuid.uuid4()),
            created_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            org_region=org_region,
            subsystem_type=subsystem_type,
            document_type=document_type,
            exact_date=exact_date.isoformat(),
        )

    def _via_tunnel(self, real_url: str) -> str:
        """Подменяет схему+хост на туннельный (если задан eis_local_proxy_url), сохраняя путь и query."""
        if not self.eis_local_proxy_url:
            return real_url
        from urllib.parse import urlsplit, urlunsplit

        proxy_parts = urlsplit(self.eis_local_proxy_url)
        real_parts = urlsplit(real_url)
        return urlunsplit((proxy_parts.scheme, proxy_parts.netloc, real_parts.path, real_parts.query, ""))

    def _run_curl(self, args: list[str], stdin_data: bytes | None = None) -> bytes:
        """
        Запускает ГОСТ-TLS-совместимый curl из КриптоПро как отдельный процесс.
        Это обходной путь для сред, где нет ни ГОСТ-плагина для системного
        OpenSSL, ни готового туннеля (stunnel) — только сам curl из состава CSP.
        """
        cmd = [self.curl_binary, "-sS", "--fail-with-body", *args]
        try:
            result = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except FileNotFoundError as exc:
            raise EISClientError(f"Не найден curl по пути {self.curl_binary}: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise EISClientError(f"curl не ответил за отведённое время: {exc}") from exc

        if result.returncode != 0:
            stderr_text = result.stderr.decode("utf-8", errors="replace")
            raise EISClientError(
                f"curl завершился с кодом {result.returncode}: {stderr_text[:1000] or result.stdout[:1000]}"
            )
        return result.stdout

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.TransportError, EISClientError)),
    )
    def _post(self, xml_body: str) -> etree._Element:
        headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": SOAP_ACTION}

        if self.curl_binary:
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
                tmp.write(xml_body.encode("utf-8"))
                tmp_path = Path(tmp.name)
            try:
                content = self._run_curl(
                    [
                        "-X", "POST",
                        "-H", f"Content-Type: {headers['Content-Type']}",
                        "-H", f"SOAPAction: {headers['SOAPAction']}",
                        "-H", "Expect:",  # отключаем Expect: 100-continue — часть серверов рвёт соединение на нём
                        "--data-binary", f"@{tmp_path}",
                        self.real_soap_url,
                    ]
                )
            finally:
                tmp_path.unlink(missing_ok=True)
        else:
            url = self._via_tunnel(self.real_soap_url)
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, content=xml_body.encode("utf-8"), headers=headers)
            if response.status_code == 401 or response.status_code == 403:
                raise EISAuthError(f"ЕИС отклонила токен (HTTP {response.status_code}). Проверьте срок действия.")
            if response.status_code != 200:
                raise EISClientError(f"ЕИС вернула HTTP {response.status_code}: {response.text[:500]}")
            content = response.content

        try:
            return etree.fromstring(content)
        except etree.XMLSyntaxError as exc:
            raise EISClientError(
                f"Не удалось распарсить ответ ЕИС как XML: {exc}. Начало ответа: {content[:300]!r}"
            ) from exc

    def request_archive(
        self,
        org_region: str,
        exact_date: date,
        document_type: str,
        subsystem_type: str = "PRIZ",
    ) -> ArchiveReference:
        """
        Запрашивает у ЕИС формирование архива документов заданного типа
        по региону заказчика за конкретную дату. Возвращает ссылку на архив
        — сам архив в этом же ответе НЕ приходит, его нужно скачать отдельно
        (см. download_archive), с тем же токеном в заголовке.
        """
        xml_body = self._build_request(org_region, subsystem_type, document_type, exact_date)
        root = self._post(xml_body)

        # Ответ приходит в SOAP-конверте; ищем archiveUrl без привязки к
        # конкретному префиксу namespace (сервис ЕИС использовал разные —
        # ns2, ip и т.д. в зависимости от версии), поэтому ищем по local-name.
        archive_url_elements = root.xpath("//*[local-name()='archiveUrl']")
        if not archive_url_elements or not archive_url_elements[0].text:
            fault_elements = root.xpath("//*[local-name()='faultstring' or local-name()='errorMessage']")
            if fault_elements:
                raise EISClientError(f"ЕИС вернула ошибку: {fault_elements[0].text}")
            raise EISClientError(
                "В ответе ЕИС не найден archiveUrl. Данных за эту дату/регион/тип может не быть, "
                "либо изменился формат ответа сервиса — нужно свериться со свежей интеграционной схемой "
                f"({self.real_soap_url}?xsd=getDocsIP-ws-api.xsd)."
            )

        return ArchiveReference(
            url=archive_url_elements[0].text.strip(),
            document_type=document_type,
            region=org_region,
            requested_date=exact_date,
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.TransportError, EISClientError)),
    )
    def download_archive(self, archive_ref: ArchiveReference) -> bytes:
        """
        Скачивает zip-архив с документами. Токен нужно передать повторно —
        ссылка сама по себе токеном не защищена, это отдельный шаг, который
        легко упустить (в паре источников это отмечено как "неочевидный момент").
        """
        if self.curl_binary:
            return self._run_curl(["-H", f"individualPerson_token: {self.token}", archive_ref.url])

        headers = {"individualPerson_token": self.token}
        url = self._via_tunnel(archive_ref.url)
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
        if response.status_code != 200:
            raise EISClientError(f"Не удалось скачать архив (HTTP {response.status_code}): {archive_ref.url}")
        return response.content
