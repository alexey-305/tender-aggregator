"""
Разбор XML-извещений о закупке (44-ФЗ) из архивов, полученных через
сервис отдачи информации ЕИС.

ВАЖНО про надёжность этого модуля: официальная XSD-схема версионируется
(структура для epNotificationEF2020 менялась несколько раз за последние
годы), и без доступа к реальному образцу XML из вашего аккаунта нельзя
дать 100% гарантию точных путей полей. Поэтому подход защитный:

1. Ищем нужные поля по имени тега (local-name), не привязываясь к
   префиксу namespace и точной глубине вложенности — это переживает
   мелкие изменения схемы.
2. Если поле не нашлось — не падаем, просто оставляем None.
3. Весь документ целиком, как есть, всегда уходит в raw_data (JSONB).
   Так что даже если типизированные поля не размаплены верно с первого
   раза, исходные данные не теряются и мапинг можно поправить позже,
   не теряя историю.

Как только у вас пойдут реальные архивы — пришлите/покажите мне пару
сырых XML-файлов извещений, и я поправлю xpath-пути на точные вместо
эвристических.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from lxml import etree

from app.models.enums import ProcurementMethod, TenderStatus
from app.services.parsers.eis.document_types import DOCUMENT_TYPE_TO_METHOD


def _find_text(root: etree._Element, *local_names: str) -> str | None:
    """Ищет первый элемент с одним из указанных имён (в порядке приоритета), возвращает текст."""
    for name in local_names:
        found = root.xpath(f".//*[local-name()='{name}']")
        if found and found[0].text and found[0].text.strip():
            return found[0].text.strip()
    return None


def _find_all_text(root: etree._Element, local_name: str) -> list[str]:
    return [el.text.strip() for el in root.xpath(f".//*[local-name()='{local_name}']") if el.text and el.text.strip()]


def _parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value.replace(" ", "").replace(",", "."))
    except InvalidOperation:
        return None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            continue
    return None


def _element_to_dict(el: etree._Element) -> dict | str | None:
    """Грубая, но надёжная конвертация XML-дерева в dict для хранения в raw_data."""
    children = list(el)
    if not children:
        return el.text.strip() if el.text and el.text.strip() else None
    result: dict = {}
    for child in children:
        tag = etree.QName(child).localname
        value = _element_to_dict(child)
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(value)
        else:
            result[tag] = value
    return result


@dataclass
class ParsedNotification:
    external_id: str | None
    title: str | None
    initial_price: Decimal | None
    okpd2_codes: list[str] = field(default_factory=list)
    customer_inn: str | None = None
    customer_name: str | None = None
    published_at: datetime | None = None
    submission_deadline: datetime | None = None
    procurement_method: ProcurementMethod = ProcurementMethod.UNKNOWN
    status: TenderStatus = TenderStatus.UNKNOWN
    raw_data: dict = field(default_factory=dict)


def parse_notification_xml(xml_bytes: bytes, document_type: str) -> ParsedNotification | None:
    """
    Разбирает один XML-файл извещения. Возвращает None, если это не
    похоже на извещение (например, служебный файл или файл подписи ЭЦП
    внутри того же архива — такие тоже встречаются).
    """
    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError:
        return None

    external_id = _find_text(root, "purchaseNumber", "notificationNumber", "regNumber", "registrationNumber")
    if not external_id:
        # Без номера закупки документ бесполезен как отдельная запись — пропускаем.
        return None

    title = _find_text(root, "purchaseObjectInfo", "notificationName", "name", "purchaseObjectInfoText")

    initial_price = _parse_decimal(
        _find_text(root, "maxPrice", "initialSum", "startPrice", "totalContractPrice", "notificationPriceInfo")
    )

    okpd2_codes = _find_all_text(root, "OKPD2Code") or _find_all_text(root, "OKPD2")

    customer_inn = _find_text(root, "INN", "inn")
    customer_name = _find_text(root, "fullName", "shortName", "customerFullName")

    published_at = _parse_datetime(_find_text(root, "publishDTInEIS", "publishDate", "createDate"))
    submission_deadline = _parse_datetime(
        _find_text(root, "collectingEndDate", "endDate", "submissionCloseDateTime")
    )

    procurement_method = DOCUMENT_TYPE_TO_METHOD.get(document_type, ProcurementMethod.UNKNOWN)

    return ParsedNotification(
        external_id=external_id,
        title=title or "(название не распознано, см. raw_data)",
        initial_price=initial_price,
        okpd2_codes=okpd2_codes,
        customer_inn=customer_inn,
        customer_name=customer_name,
        published_at=published_at,
        submission_deadline=submission_deadline,
        procurement_method=procurement_method,
        status=TenderStatus.UNKNOWN,  # статус в извещении напрямую не всегда указан явно — уточним по мере разбора реальных данных
        raw_data=_element_to_dict(root) or {},
    )
