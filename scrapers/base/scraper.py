from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ScraperInterface(ABC):
    @abstractmethod
    def search(self, search_term: str) -> List[str]: ...

    @abstractmethod
    def scrape_data(self, url: str) -> Dict[str, Any]: ...

    @abstractmethod
    def update_data(self, product: Dict[str, Any]) -> Dict[str, Any]: ...
