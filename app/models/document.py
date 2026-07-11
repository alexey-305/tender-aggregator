import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TenderDocument(Base):
    """
    Документация закупки (техзадание, проект контракта, извещение и т.д.).
    Файлы сами по себе не храним в БД — держим ссылку на источник и,
    опционально, путь до копии в объектном хранилище (заполняется позже,
    когда появится сервис скачивания/архивации документов).
    """

    __tablename__ = "tender_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenders.id"), nullable=False)
    tender: Mapped["Tender"] = relationship(back_populates="documents")

    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # pdf, docx, zip...
    storage_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)  # путь в объектном хранилище

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
