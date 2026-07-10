class EISService:

    def get_tenders(self):

        return [
            {
                "registry_number": "0373100001026000001",
                "name": "Поставка компьютерной техники",
                "customer": "Министерство тестовое",
                "price": 2500000,
                "region": "Москва",
                "status": "Прием заявок"
            },
            {
                "registry_number": "0360100001026000002",
                "name": "Закупка оборудования",
                "customer": "Государственное учреждение",
                "price": 870000,
                "region": "Саратовская область",
                "status": "Размещено"
            }
        ]