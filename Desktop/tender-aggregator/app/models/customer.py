import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Customer(Base):
    """
    Заказчик/организатор закупки. Один заказчик может встречаться в разных
    источниках под разными идентификаторами — связываем по ИНН.
    """

    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    inn: Mapped[str | None] = mapped_column(String(12), index=True, nullable=True)
    kpp: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ogrn: Mapped[str | None] = mapped_column(String(15), nullable=True)

    name: Mapped[str] = mapped_column(String(1024), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    region: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tenders: Mapped[list["Tender"]] = relationship(back_populates="customer")
