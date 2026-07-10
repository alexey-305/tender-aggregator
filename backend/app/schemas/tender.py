from pydantic import BaseModel
from datetime import datetime


class TenderBase(BaseModel):

    registry_number: str

    name: str

    customer: str

    customer_inn: str | None = None

    law_type: str | None = None

    price: float | None = None

    region: str | None = None

    status: str | None = None

    etp_name: str | None = None

    url: str | None = None

    publish_date: datetime | None = None

    deadline: datetime | None = None


class TenderCreate(TenderBase):
    pass


class TenderResponse(TenderBase):

    id: int

    created_at: datetime

    class Config:
        from_attributes = True