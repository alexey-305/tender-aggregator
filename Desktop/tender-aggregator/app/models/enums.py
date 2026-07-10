import enum


class TenderSource(str, enum.Enum):
    """Источник данных о закупке. Расширяется по мере добавления интеграций."""

    EIS_44FZ = "eis_44fz"
    EIS_223FZ = "eis_223fz"
    EIS_615PP = "eis_615pp"  # капремонт
    B2B_CENTER = "b2b_center"
    FABRIKANT = "fabrikant"
    RTS_TENDER = "rts_tender"
    SBERBANK_AST = "sberbank_ast"
    BANKRUPTCY_EFRSB = "bankruptcy_efrsb"
    OTHER = "other"


class ProcurementMethod(str, enum.Enum):
    """Способ определения поставщика — унифицированный поверх разных источников."""

    ELECTRONIC_AUCTION = "electronic_auction"
    OPEN_TENDER = "open_tender"
    OPEN_TENDER_LIMITED = "open_tender_limited"  # конкурс с огр. участием
    TWO_STAGE_TENDER = "two_stage_tender"
    REQUEST_FOR_QUOTATIONS = "request_for_quotations"  # запрос котировок
    REQUEST_FOR_PROPOSALS = "request_for_proposals"  # запрос предложений
    SINGLE_SUPPLIER = "single_supplier"
    COMMERCIAL_OTHER = "commercial_other"
    UNKNOWN = "unknown"


class TenderStatus(str, enum.Enum):
    PUBLISHED = "published"
    CLARIFICATION = "clarification"  # идёт приём разъяснений
    SUBMISSION_OPEN = "submission_open"
    SUBMISSION_CLOSED = "submission_closed"
    SUMMARIZING = "summarizing"  # подведение итогов
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ProcurementLaw(str, enum.Enum):
    FZ_44 = "44-fz"
    FZ_223 = "223-fz"
    PP_615 = "615-pp"
    COMMERCIAL = "commercial"
    BANKRUPTCY = "bankruptcy"
