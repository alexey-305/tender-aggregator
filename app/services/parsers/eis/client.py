"""
РљР»РёРµРЅС‚ SOAP-СЃРµСЂРІРёСЃР° РѕС‚РґР°С‡Рё РёРЅС„РѕСЂРјР°С†РёРё Р•РРЎ (getDocsIP).

РџСЂРёС€С‘Р» РЅР° СЃРјРµРЅСѓ FTP-СЃРµСЂРІРµСЂСѓ zakupki.gov.ru, Р·Р°РєСЂС‹С‚РѕРјСѓ СЃ 01.01.2025.
Р¤РѕСЂРјР°С‚ Р·Р°РїСЂРѕСЃР° РїРѕРґС‚РІРµСЂР¶РґС‘РЅ РїРѕ РЅРµСЃРєРѕР»СЊРєРёРј РЅРµР·Р°РІРёСЃРёРјС‹Рј РїСЂР°РєС‚РёС‡РµСЃРєРёРј
РёСЃС‚РѕС‡РЅРёРєР°Рј (РѕС„РёС†РёР°Р»СЊРЅР°СЏ РёРЅСЃС‚СЂСѓРєС†РёСЏ Р•РРЎ + РѕРїС‹С‚ СЂР°Р·СЂР°Р±РѕС‚С‡РёРєРѕРІ РІ 2024-2025),
РЅРѕ РќР• РїСЂРѕС‚РµСЃС‚РёСЂРѕРІР°РЅ РїСЂРѕС‚РёРІ СЂРµР°Р»СЊРЅРѕРіРѕ СЃРµСЂРІРёСЃР° РёР· СЌС‚РѕРіРѕ РѕРєСЂСѓР¶РµРЅРёСЏ вЂ”
zakupki.gov.ru РЅРµРґРѕСЃС‚СѓРїРµРЅ РёР· РїРµСЃРѕС‡РЅРёС†С‹, РіРґРµ РїРёСЃР°Р»СЃСЏ СЌС‚РѕС‚ РєРѕРґ.
РџРµСЂРІС‹Р№ СЂРµР°Р»СЊРЅС‹Р№ РїСЂРѕРіРѕРЅ РЅСѓР¶РЅРѕ РґРµР»Р°С‚СЊ РІ РІР°С€РµРј РѕРєСЂСѓР¶РµРЅРёРё СЃ РІР°С€РёРј С‚РѕРєРµРЅРѕРј
Рё РІРЅРёРјР°С‚РµР»СЊРЅРѕ СЃРјРѕС‚СЂРµС‚СЊ РЅР° С‚РµРєСЃС‚ РѕС€РёР±РєРё, РµСЃР»Рё РѕРЅР° Р±СѓРґРµС‚ вЂ” СЃРµСЂРІРёСЃ Сѓ Р•РРЎ
РёСЃС‚РѕСЂРёС‡РµСЃРєРё РЅРµСЃС‚Р°Р±РёР»РµРЅ Рё РјРµРЅСЏР» Р°РґСЂРµСЃР°/РїРѕРІРµРґРµРЅРёРµ РЅРµСЃРєРѕР»СЊРєРѕ СЂР°Р· Р·Р° 2025 РіРѕРґ.
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

# Р РµР°Р»СЊРЅРѕРµ Р·РЅР°С‡РµРЅРёРµ SOAPAction РІР·СЏС‚Рѕ РёР· Р¶РёРІРѕРіРѕ WSDL СЃРµСЂРІРёСЃР° (РїСЂРѕРІРµСЂРµРЅРѕ:
# GET .../getDocsIP?wsdl РІРµСЂРЅСѓР» 200 Рё СЌС‚Рѕ Р·РЅР°С‡РµРЅРёРµ РІ wsdl:binding).
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

# РџРѕСЂСЏРґРѕРє РґРѕС‡РµСЂРЅРёС… С‚РµРіРѕРІ РІ selectionParams РІР°Р¶РµРЅ РґР»СЏ Р•РРЎ вЂ” СЃРµСЂРІРµСЂ РѕС‚РєР»РѕРЅСЏРµС‚
# Р·Р°РїСЂРѕСЃ СЃ "РїСЂР°РІРёР»СЊРЅС‹РјРё" С‚РµРіР°РјРё РІ "РЅРµРїСЂР°РІРёР»СЊРЅРѕРј" РїРѕСЂСЏРґРєРµ (СЌС‚Рѕ РїРѕРґС‚РІРµСЂР¶РґРµРЅРѕ
# РЅР° РїСЂР°РєС‚РёРєРµ РЅРµСЃРєРѕР»СЊРєРёРјРё РЅРµР·Р°РІРёСЃРёРјРѕ РґСЂСѓРі РѕС‚ РґСЂСѓРіР° СЂР°Р·СЂР°Р±РѕС‚С‡РёРєР°РјРё).


class EISClientError(Exception):
    """РћС€РёР±РєР° РїСЂРё РѕР±СЂР°С‰РµРЅРёРё Рє СЃРµСЂРІРёСЃСѓ РѕС‚РґР°С‡Рё РёРЅС„РѕСЂРјР°С†РёРё Р•РРЎ."""


class EISAuthError(EISClientError):
    """РўРѕРєРµРЅ РЅРµ РїСЂРёРЅСЏС‚ СЃРµСЂРІРёСЃРѕРј (РїСЂРѕСЃСЂРѕС‡РµРЅ/РЅРµРІР°Р»РёРґРµРЅ/РЅРµ С‚РѕС‚ С‚РёРї СЃРµСЂРІРёСЃР°)."""


@dataclass
class ArchiveReference:
    """РЎСЃС‹Р»РєР° РЅР° Р°СЂС…РёРІ СЃ РґРѕРєСѓРјРµРЅС‚Р°РјРё, РїРѕР»СѓС‡РµРЅРЅР°СЏ РІ РѕС‚РІРµС‚ РЅР° Р·Р°РїСЂРѕСЃ."""

    url: str
    document_type: str
    region: str
    requested_date: date


class EISClient:
    def __init__(self, token: str | None = None, soap_url: str | None = None) -> None:
        self.token = token or settings.eis_token
        self.real_soap_url = soap_url or settings.eis_soap_url
        # Р•СЃР»Рё Р·Р°РґР°РЅ Р»РѕРєР°Р»СЊРЅС‹Р№ Р“РћРЎРў-TLS С‚СѓРЅРЅРµР»СЊ вЂ” С„РёР·РёС‡РµСЃРєРё С…РѕРґРёРј С‚СѓРґР° РЅР°РїСЂСЏРјСѓСЋ (httpx).
        self.eis_local_proxy_url = settings.eis_local_proxy_url
        # Р•СЃР»Рё Р·Р°РґР°РЅ Р“РћРЎРў-СЃРѕРІРјРµСЃС‚РёРјС‹Р№ curl (РЅР°РїСЂРёРјРµСЂ, РёР· РљСЂРёРїС‚РѕРџСЂРѕ CSP:
        # /opt/cprocsp/bin/curl) вЂ” С…РѕРґРёРј С‡РµСЂРµР· subprocess-РІС‹Р·РѕРІ СЌС‚РѕРіРѕ curl,
        # С‚.Рє. РѕР±С‹С‡РЅС‹Р№ httpx/OpenSSL Р“РћРЎРў-TLS РЅРµ РїРѕРґРґРµСЂР¶РёРІР°РµС‚.
        self.curl_binary = settings.eis_curl_binary
        if not self.token:
            raise EISAuthError(
                "РќРµ Р·Р°РґР°РЅ EIS_TOKEN. РџРѕР»СѓС‡РёС‚СЊ С‚РѕРєРµРЅ: Р»РёС‡РЅС‹Р№ РєР°Р±РёРЅРµС‚ Р•РРЎ -> "
                "pmd.zakupki.gov.ru/pmd/lk/token (С‚СЂРµР±СѓРµС‚СЃСЏ РґРµР№СЃС‚РІСѓСЋС‰Р°СЏ Р­Р¦Рџ)."
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
        """РџРѕРґРјРµРЅСЏРµС‚ СЃС…РµРјСѓ+С…РѕСЃС‚ РЅР° С‚СѓРЅРЅРµР»СЊРЅС‹Р№ (РµСЃР»Рё Р·Р°РґР°РЅ eis_local_proxy_url), СЃРѕС…СЂР°РЅСЏСЏ РїСѓС‚СЊ Рё query."""
        if not self.eis_local_proxy_url:
            return real_url
        from urllib.parse import urlsplit, urlunsplit

        proxy_parts = urlsplit(self.eis_local_proxy_url)
        real_parts = urlsplit(real_url)
        return urlunsplit((proxy_parts.scheme, proxy_parts.netloc, real_parts.path, real_parts.query, ""))

    def _run_curl(self, args: list[str], stdin_data: bytes | None = None) -> bytes:
        """
        Р—Р°РїСѓСЃРєР°РµС‚ Р“РћРЎРў-TLS-СЃРѕРІРјРµСЃС‚РёРјС‹Р№ curl РёР· РљСЂРёРїС‚РѕРџСЂРѕ РєР°Рє РѕС‚РґРµР»СЊРЅС‹Р№ РїСЂРѕС†РµСЃСЃ.
        Р­С‚Рѕ РѕР±С…РѕРґРЅРѕР№ РїСѓС‚СЊ РґР»СЏ СЃСЂРµРґ, РіРґРµ РЅРµС‚ РЅРё Р“РћРЎРў-РїР»Р°РіРёРЅР° РґР»СЏ СЃРёСЃС‚РµРјРЅРѕРіРѕ
        OpenSSL, РЅРё РіРѕС‚РѕРІРѕРіРѕ С‚СѓРЅРЅРµР»СЏ (stunnel) вЂ” С‚РѕР»СЊРєРѕ СЃР°Рј curl РёР· СЃРѕСЃС‚Р°РІР° CSP.
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
            raise EISClientError(f"РќРµ РЅР°Р№РґРµРЅ curl РїРѕ РїСѓС‚Рё {self.curl_binary}: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise EISClientError(f"curl РЅРµ РѕС‚РІРµС‚РёР» Р·Р° РѕС‚РІРµРґС‘РЅРЅРѕРµ РІСЂРµРјСЏ: {exc}") from exc

        if result.returncode != 0:
            stderr_text = result.stderr.decode("utf-8", errors="replace")
            raise EISClientError(
                f"curl Р·Р°РІРµСЂС€РёР»СЃСЏ СЃ РєРѕРґРѕРј {result.returncode}: {stderr_text[:1000] or result.stdout[:1000]}"
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
                        "-H", "Expect:",  # РѕС‚РєР»СЋС‡Р°РµРј Expect: 100-continue вЂ” С‡Р°СЃС‚СЊ СЃРµСЂРІРµСЂРѕРІ СЂРІС‘С‚ СЃРѕРµРґРёРЅРµРЅРёРµ РЅР° РЅС‘Рј
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
                raise EISAuthError(f"Р•РРЎ РѕС‚РєР»РѕРЅРёР»Р° С‚РѕРєРµРЅ (HTTP {response.status_code}). РџСЂРѕРІРµСЂСЊС‚Рµ СЃСЂРѕРє РґРµР№СЃС‚РІРёСЏ.")
            if response.status_code != 200:
                raise EISClientError(f"Р•РРЎ РІРµСЂРЅСѓР»Р° HTTP {response.status_code}: {response.text[:500]}")
            content = response.content

        try:
            return etree.fromstring(content)
        except etree.XMLSyntaxError as exc:
            raise EISClientError(
                f"РќРµ СѓРґР°Р»РѕСЃСЊ СЂР°СЃРїР°СЂСЃРёС‚СЊ РѕС‚РІРµС‚ Р•РРЎ РєР°Рє XML: {exc}. РќР°С‡Р°Р»Рѕ РѕС‚РІРµС‚Р°: {content[:300]!r}"
            ) from exc

    def request_archive(
        self,
        org_region: str,
        exact_date: date,
        document_type: str,
        subsystem_type: str = "PRIZ",
    ) -> ArchiveReference:
        """
        Р—Р°РїСЂР°С€РёРІР°РµС‚ Сѓ Р•РРЎ С„РѕСЂРјРёСЂРѕРІР°РЅРёРµ Р°СЂС…РёРІР° РґРѕРєСѓРјРµРЅС‚РѕРІ Р·Р°РґР°РЅРЅРѕРіРѕ С‚РёРїР°
        РїРѕ СЂРµРіРёРѕРЅСѓ Р·Р°РєР°Р·С‡РёРєР° Р·Р° РєРѕРЅРєСЂРµС‚РЅСѓСЋ РґР°С‚Сѓ. Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃСЃС‹Р»РєСѓ РЅР° Р°СЂС…РёРІ
        вЂ” СЃР°Рј Р°СЂС…РёРІ РІ СЌС‚РѕРј Р¶Рµ РѕС‚РІРµС‚Рµ РќР• РїСЂРёС…РѕРґРёС‚, РµРіРѕ РЅСѓР¶РЅРѕ СЃРєР°С‡Р°С‚СЊ РѕС‚РґРµР»СЊРЅРѕ
        (СЃРј. download_archive), СЃ С‚РµРј Р¶Рµ С‚РѕРєРµРЅРѕРј РІ Р·Р°РіРѕР»РѕРІРєРµ.
        """
        xml_body = self._build_request(org_region, subsystem_type, document_type, exact_date)
        root = self._post(xml_body)

        # РћС‚РІРµС‚ РїСЂРёС…РѕРґРёС‚ РІ SOAP-РєРѕРЅРІРµСЂС‚Рµ; РёС‰РµРј archiveUrl Р±РµР· РїСЂРёРІСЏР·РєРё Рє
        # РєРѕРЅРєСЂРµС‚РЅРѕРјСѓ РїСЂРµС„РёРєСЃСѓ namespace (СЃРµСЂРІРёСЃ Р•РРЎ РёСЃРїРѕР»СЊР·РѕРІР°Р» СЂР°Р·РЅС‹Рµ вЂ”
        # ns2, ip Рё С‚.Рґ. РІ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ РІРµСЂСЃРёРё), РїРѕСЌС‚РѕРјСѓ РёС‰РµРј РїРѕ local-name.
        archive_url_elements = root.xpath("//*[local-name()='archiveUrl']")
        if not archive_url_elements or not archive_url_elements[0].text:
            fault_elements = root.xpath("//*[local-name()='faultstring' or local-name()='errorMessage']")
            if fault_elements:
                raise EISClientError(f"Р•РРЎ РІРµСЂРЅСѓР»Р° РѕС€РёР±РєСѓ: {fault_elements[0].text}")
            raise EISClientError(
                "Р’ РѕС‚РІРµС‚Рµ Р•РРЎ РЅРµ РЅР°Р№РґРµРЅ archiveUrl. Р”Р°РЅРЅС‹С… Р·Р° СЌС‚Сѓ РґР°С‚Сѓ/СЂРµРіРёРѕРЅ/С‚РёРї РјРѕР¶РµС‚ РЅРµ Р±С‹С‚СЊ, "
                "Р»РёР±Рѕ РёР·РјРµРЅРёР»СЃСЏ С„РѕСЂРјР°С‚ РѕС‚РІРµС‚Р° СЃРµСЂРІРёСЃР° вЂ” РЅСѓР¶РЅРѕ СЃРІРµСЂРёС‚СЊСЃСЏ СЃРѕ СЃРІРµР¶РµР№ РёРЅС‚РµРіСЂР°С†РёРѕРЅРЅРѕР№ СЃС…РµРјРѕР№ "
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
        "Скачивает zip-архив с документами."
        if self.curl_binary:
            return self._run_curl(["-H", f"individualPerson_token: {self.token}", archive_ref.url])

        headers = {"individualPerson_token": self.token}
        url = self._via_tunnel(archive_ref.url)
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
        if response.status_code != 200:
            raise EISClientError(f"Не удалось скачать архив (HTTP {response.status_code}): {archive_ref.url}")
        return response.content

    def download_archive_raw(self, url: str) -> bytes:
        if self.curl_binary:
            return self._run_curl(["-H", f"individualPerson_token: {self.token}", url])
        headers = {"individualPerson_token": self.token}
        proxy_url = self._via_tunnel(url)
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(proxy_url, headers=headers)
        if response.status_code != 200:
            raise EISClientError(f"Не удалось скачать архив (HTTP {response.status_code}): {url}")
        return response.content

