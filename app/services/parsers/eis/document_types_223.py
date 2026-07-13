from app.models.enums import ProcurementMethod

NOTIFICATION_SUBSYSTEM_TYPE_223 = "RI223"

DOCUMENT_TYPE_TO_METHOD_223 = {
    "purchaseNotice": ProcurementMethod.OPEN_TENDER,
}

DEFAULT_DOCUMENT_TYPES_223 = [
    "purchaseNotice",
]