import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ProcurementLaw, ProcurementMethod, TenderSource, TenderStatus


class Tender(Base):
    """
    Нормализованная карточка закупки — единая точка входа для всех источников.

    Принцип: общие для всех площадок поля — отдельные типизированные колонки
    (по ним строится поиск/фильтрация/аналитика). Всё специфичное для
    конкретного источника (нестандартные поля, доп. атрибуты площадки) —
    в raw_data (JSONB), чтобы не переделывать схему при добавлении
    нового источника.
    """

    __tablename__ = "tenders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # --- Идентификация и происхождение ---
    source: Mapped[TenderSource] = mapped_column(Enum(TenderSource, name="tender_source"), index=True, nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)  # номер закупки на площадке
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    law: Mapped[ProcurementLaw] = mapped_column(Enum(ProcurementLaw, name="procurement_law"), index=True, nullable=False)

    # --- Основное содержание ---
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    okpd2_codes: Mapped[list[str]] = mapped_column(ARRAY(String(20)), default=list, server_default="{}")
    okved_codes: Mapped[list[str]] = mapped_column(ARRAY(String(20)), default=list, server_default="{}")

    procurement_method: Mapped[ProcurementMethod] = mapped_column(
        Enum(ProcurementMethod, name="procurement_method"), index=True, nullable=False
    )
    status: Mapped[TenderStatus] = mapped_column(
        Enum(TenderStatus, name="tender_status"), index=True, default=TenderStatus.UNKNOWN
    )

    # --- Заказчик ---
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    customer: Mapped["Customer"] = relationship(back_populates="tenders")

    # --- Деньги ---
    initial_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)  # НМЦК
    currency: Mapped[str] = mapped_column(String(3), default="RUB")

    # --- География ---
    region: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    delivery_place: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Даты (ключевые для уведомлений и сортировки) ---
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    submission_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    summarizing_date: Mapped[date | None] = mapped_column(nullable=True)

    # --- Требования к участникам (для будущего ИИ-ассистента) ---
    requires_smp_sonko: Mapped[bool] = mapped_column(default=False)  # закупка среди СМП/СОНКО
    security_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)  # обеспечение заявки

    # --- Технические поля ---
    raw_data: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # синхронизация с OpenSearch

    documents: Mapped[list["TenderDocument"]] = relationship(back_populates="tender", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_tender_source_external_id"),
        Index("ix_tender_law_status", "law", "status"),
        Index("ix_tender_okpd2", "okpd2_codes", postgresql_using="gin"),
    )
