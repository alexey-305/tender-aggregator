from abc import ABC, abstractmethod


class BaseLoader(ABC):
    """
    Базовый интерфейс любого источника закупок.
    ЕИС, ЭТП и коммерческие площадки
    должны реализовывать этот интерфейс.
    """

    @abstractmethod
    def load(self) -> list[dict]:
        pass