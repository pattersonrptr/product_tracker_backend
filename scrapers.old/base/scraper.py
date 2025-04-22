from abc import ABC, abstractmethod


class Scraper(ABC):
    @abstractmethod
    def search(self, search_term: str) -> list[str]: ...

    @abstractmethod
    def scrape_data(self, url: str) -> dict: ...

    @abstractmethod
    def update_data(self, product: dict) -> dict: ...
