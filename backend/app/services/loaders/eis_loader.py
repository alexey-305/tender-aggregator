from datetime import datetime

from services.loaders.base import BaseLoader


class EISLoader(BaseLoader):

    def load(self) -> list[dict]:

        """
        Временная реализация.

        Сейчас возвращает тестовые данные.
        Следующим этапом заменим
        на реальный источник ЕИС.
        """

        return [
            {
                "registry_number": "0373100001026000005",
                "name": "Поставка серверного оборудования",
                "customer": "Федеральное учреждение связи",
                "customer_inn": "7700000001",
                "law_type": "44-ФЗ",
                "price": 4200000,
                "region": "Москва",
                "status": "Прием заявок",
                "etp_name": "РТС-тендер",
                "url": "https://zakupki.gov.ru",
                "publish_date": datetime.utcnow(),
                "deadline": datetime.utcnow()
            },
            {
                "registry_number": "0160100001026000006",
                "name": "Закупка программного обеспечения",
                "customer": "Министерство информационных технологий",
                "customer_inn": "6400000002",
                "law_type": "223-ФЗ",
                "price": 1800000,
                "region": "Саратовская область",
                "status": "Размещено",
                "etp_name": "ЕЭТП",
                "url": "https://zakupki.gov.ru",
                "publish_date": datetime.utcnow(),
                "deadline": datetime.utcnow()
            }
        ]