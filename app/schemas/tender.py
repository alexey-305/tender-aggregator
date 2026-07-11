import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import ProcurementLaw, ProcurementMethod, TenderSource, TenderStatus


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inn: str | None = None
    name: str
    region: str | None = None


class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: TenderSource
    external_id: str
    source_url: str | None = None
    law: ProcurementLaw

    title: str
    okpd2_codes: list[str] = []
    procurement_method: ProcurementMethod
    status: TenderStatus

    customer: CustomerOut | None = None

    initial_price: Decimal | None = None
    currency: str = "RUB"

    region: str | None = None

    published_at: datetime | None = None
    submission_deadline: datetime | None = None
    summarizing_date: date | None = None

    requires_smp_sonko: bool = False
    security_amount: Decimal | None = None


class TenderSearchParams(BaseModel):
    query: str | None = None
    okpd2: list[str] | None = None
    region: list[str] | None = None
    law: list[ProcurementLaw] | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    deadline_from: datetime | None = None
    deadline_to: datetime | None = None
    page: int = 1
    page_size: int = 20
