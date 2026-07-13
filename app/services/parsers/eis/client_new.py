
Клиент SOAP-сервиса отдачи информации ЕИС (getDocsLE/getDocsIP).
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

SOAP_ACTION_LE = "http://zakupki.gov.ru/fz44/get-docs-le/ws"
SOAP_ACTION_IP = "http://zakupki.gov.ru/fz44/queue/ws/get-docs-ip"

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


class EISClientError(Exception):
    """Ошибка при обращении к сервису отдачи информации ЕИС."""


class EISAuthError(EISClientError):
    """Токен не принят сервисом."""


@dataclass
class ArchiveReference:
    url: str
    document_type: str
    region: str
    requested_date: date


class EISClient:
    def __init__(self, token: str | None = None, soap_url: str | None = None) -> None:
        self.token = token or settings.eis_token
        self.real_soap_url = soap_url or settings.eis_soap_url.replace("/getDocsIP", "/getDocsLE")
        self.eis_local_proxy_url = settings.eis_local_proxy_url
        self.curl_binary = settings.eis_curl_binary
        if not self.token:
            raise EISAuthError("Не задан EIS_TOKEN.")

    def _build_request(self, org_region: str, subsystem_type: str, document_type: str, exact_date: date, use_doc223: bool = False) -> str:
        xml_body = SOAP_ENVELOPE_TEMPLATE.format(
            namespace=settings.eis_ws_namespace,
            token=self.token,
            request_id=str(uuid.uuid4()),
            created_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            org_region=org_region,
            subsystem_type=subsystem_type,
            document_type=document_type,
            exact_date=exact_date.isoformat(),
        )
        if use_doc223:
            return xml_body.replace("<documentType44>", "<documentType223>").replace("</documentType44>", "</documentType223>")
        return xml_body

    def _via_tunnel(self, real_url: str) -> str:
        if not self.eis_local_proxy_url:
            return real_url
        from urllib.parse import urlsplit, urlunsplit
        proxy_parts = urlsplit(self.eis_local_proxy_url)
        real_parts = urlsplit(real_url)
        return urlunsplit((proxy_parts.scheme, proxy_parts.netloc, real_parts.path, real_parts.query, ""))

    def _run_curl(self, args: list[str], stdin_data: bytes | None = None) -> bytes:
        cmd = [self.curl_binary, "-sS", "--fail-with-body", *args]
        try:
            result = subprocess.run(cmd, input=stdin_data, capture_output=True, timeout=120, check=False)
        except FileNotFoundError as exc:
            raise EISClientError(f"Не найден curl: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise EISClientError(f"curl timeout: {exc}") from exc
        if result.returncode != 0:
            raise EISClientError(f"curl error {result.returncode}")
        return result.stdout

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=30), retry=retry_if_exception_type((httpx.TransportError, EISClientError)))
    def _post(self, xml_body: str, action_header: str = SOAP_ACTION_LE) -> etree._Element:
        headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": action_header}
        if self.curl_binary:
            with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
                tmp.write(xml_body.encode("utf-8"))
                tmp_path = Path(tmp.name)
            try:
                content = self._run_curl(["-X", "POST", "-H", f"Content-Type: {headers['Content-Type']}", "-H", f"SOAPAction: {action_header}", "-H", "Expect:", "--data-binary", f"@{tmp_path}", self.real_soap_url])
            finally:
                tmp_path.unlink(missing_ok=True)
        else:
            url = self._via_tunnel(self.real_soap_url)
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, content=xml_body.encode("utf-8"), headers=headers)
            if response.status_code in (401, 403):
                raise EISAuthError(f"Token rejected (HTTP {response.status_code})")
            if response.status_code != 200:
                raise EISClientError(f"HTTP {response.status_code}: {response.text[:500]}")
            content = response.content
        try:
            return etree.fromstring(content)
        except etree.XMLSyntaxError as exc:
            raise EISClientError(f"XML parse error: {exc}")

    def request_archive(self, org_region: str, exact_date: date, document_type: str, subsystem_type: str = "PRIZ") -> ArchiveReference:
        xml_body = self._build_request(org_region, subsystem_type, document_type, exact_date)
        root = self._post(xml_body)
        archive_url_elements = root.xpath("//*[local-name()='archiveUrl']")
        if not archive_url_elements or not archive_url_elements[0].text:
            fault_elements = root.xpath("//*[local-name()='faultstring' or local-name()='errorMessage']")
            if fault_elements:
                raise EISClientError(f"EIS error: {fault_elements[0].text}")
            raise EISClientError("archiveUrl not found")
        return ArchiveReference(url=archive_url_elements[0].text.strip(), document_type=document_type, region=org_region, requested_date=exact_date)

    def download_archive(self, archive_ref: ArchiveReference) -> bytes:
        if self.curl_binary:
            return self._run_curl(["-H", f"individualPerson_token: {self.token}", archive_ref.url])
        headers = {"individualPerson_token": self.token}
        url = self._via_tunnel(archive_ref.url)
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
        if response.status_code != 200:
            raise EISClientError(f"Download failed (HTTP {response.status_code})")
        return response.content

    def download_archive_raw(self, url: str) -> bytes:
        if self.curl_binary:
            return self._run_curl(["-H", f"individualPerson_token: {self.token}", url])
        headers = {"individualPerson_token": self.token}
        proxy_url = self._via_tunnel(url)
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(proxy_url, headers=headers)
        if response.status_code != 200:
            raise EISClientError(f"Download failed (HTTP {response.status_code})")
        return response.content

    def request_archive_223_le(self, org_region: str, exact_date: date, document_type: str, subsystem_type: str = "RI223") -> ArchiveReference:
        print("=== 223 SOAP REQUEST ===")
        xml_body = self._build_request(org_region, subsystem_type, document_type, exact_date, use_doc223=True)
        print(xml_body[:800])
        root = self._post(xml_body, action_header=SOAP_ACTION_LE)
        print("=== 223 RESPONSE ===")
        print(etree.tostring(root, pretty_print=True).decode()[:800])
        archive_url_elements = root.xpath("//*[local-name()='archiveUrl']")
        if not archive_url_elements or not archive_url_elements[0].text:
            fault = root.xpath("//*[local-name()='faultstring' or local-name()='errorMessage']")
            if fault:
                raise EISClientError(f"EIS error: {fault[0].text}")
            raise EISClientError("archiveUrl not found in 223-FZ response")
        return ArchiveReference(url=archive_url_elements[0].text.strip(), document_type=document_type, region=org_region, requested_date=exact_date)