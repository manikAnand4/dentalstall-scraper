from abc import ABC, abstractmethod

class NotifierBase(ABC):
    @abstractmethod
    def notify_scraping_complete(self, products_count: int, updated_count: int) -> None:
        pass
