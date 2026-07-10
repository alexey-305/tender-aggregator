from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)

    # Номер закупки ЕИС
    registry_number = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    # Наименование закупки
    name = Column(
        String,
        nullable=False
    )

    # Заказчик
    customer = Column(
        String,
        nullable=False
    )

    # ИНН заказчика (будет из ЕИС)
    customer_inn = Column(
        String,
        nullable=True
    )

    # Закон
    # 44-ФЗ / 223-ФЗ
    law_type = Column(
        String,
        nullable=True
    )

    # Цена
    price = Column(
        Float,
        nullable=True
    )

    # Регион
    region = Column(
        String,
        nullable=True
    )

    # Статус закупки
    status = Column(
        String,
        nullable=True
    )

    # Электронная площадка
    etp_name = Column(
        String,
        nullable=True
    )

    # Ссылка на закупку
    url = Column(
        String,
        nullable=True
    )

    # Дата публикации
    publish_date = Column(
        DateTime,
        nullable=True
    )

    # Дата окончания подачи заявок
    deadline = Column(
        DateTime,
        nullable=True
    )

    # Когда загрузили в систему
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )