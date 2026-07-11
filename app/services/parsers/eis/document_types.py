"""
Справочник кодов documentType44, используемых в запросах к сервису отдачи
информации ЕИС (getDocsIP/getDocsLE).

Источник кодов — "Инструкция по использованию сервисов отдачи информации
и документов, размещенных на официальном сайте ЕИС" (Приложение 2).
Список НЕ полный — включены только типы, релевантные для агрегатора закупок
на старте (извещения). Расширяется по мере необходимости: планы-графики,
протоколы, контракты и т.д. живут в raw_data, даже если этого типа ещё нет
в маппинге ниже — просто procurement_method будет UNKNOWN, потерь данных нет.
"""

from app.models.enums import ProcurementMethod

# documentType44 -> способ определения поставщика
DOCUMENT_TYPE_TO_METHOD: dict[str, ProcurementMethod] = {
    "epNotificationEF2020": ProcurementMethod.ELECTRONIC_AUCTION,       # электронный аукцион
    "epNotificationEP2020": ProcurementMethod.OPEN_TENDER,              # электронный конкурс
    "epNotificationEPO2020": ProcurementMethod.OPEN_TENDER_LIMITED,     # конкурс с огр. участием
    "epNotificationEZK2020": ProcurementMethod.REQUEST_FOR_QUOTATIONS,  # запрос котировок в электр. форме
    "epNotificationEZP2020": ProcurementMethod.REQUEST_FOR_PROPOSALS,   # запрос предложений в электр. форме
    "epNotificationED2020": ProcurementMethod.TWO_STAGE_TENDER,         # двухэтапный конкурс
    "notificationSingleCustomer": ProcurementMethod.SINGLE_SUPPLIER,    # закупка у ед. поставщика
}

# subsystemType, за который отвечает извещение о закупке (а не план-график/контракт/etc.)
NOTIFICATION_SUBSYSTEM_TYPE = "PRIZ"

# Набор документов, с которых мы начинаем синхронизацию — самые частотные способы закупки.
# Остальные типы можно добавить сюда позже без изменения кода клиента.
DEFAULT_DOCUMENT_TYPES: list[str] = [
    "epNotificationEF2020",
    "epNotificationEP2020",
    "epNotificationEZK2020",
]
